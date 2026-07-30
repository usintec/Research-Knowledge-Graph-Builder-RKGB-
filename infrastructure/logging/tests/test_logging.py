"""Unit tests for the RKGB Logging & Observability Framework.

Covers:
    * Logger creation via LoggerFactory
    * Structured log entries (event dict shape)
    * Correlation context propagation
    * Context inheritance (with_pipeline, with_stage, etc.)
    * Log level filtering (LogLevelFilter)
    * Formatter selection (console vs JSON)
    * Configuration integration (LoggingConfig → LoggingManager)
    * Exception logging (ExceptionInfo capture)
"""

from __future__ import annotations

import logging
import re

import pytest
import structlog

from infrastructure.config.models.logging import LogFileConfig, LogFormat, LogLevel, LoggingConfig
from infrastructure.logging.bootstrap import build_test_logging_manager
from infrastructure.logging.context import (
    clear_correlation_context,
    get_correlation_context,
    set_correlation_context,
)
from infrastructure.logging.correlation import (
    UUIDCorrelationProvider,
    generate_correlation_id,
    generate_trace_id,
)
from infrastructure.logging.exceptions import (
    FormatterNotFoundError,
    LoggingNotInitialisedError,
)
from infrastructure.logging.factory import LoggerFactory
from infrastructure.logging.filters import LogLevelFilter, SensitiveDataFilter
from infrastructure.logging.formatter import ConsoleFormatter, JSONFormatter, build_formatter
from infrastructure.logging.logger import RKGBLogger
from infrastructure.logging.manager import LoggingManager
from infrastructure.logging.models.context import CorrelationContext
from infrastructure.logging.models.log_entry import ExceptionInfo, LogEntry


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_structlog_and_context():
    """Reset structlog configuration and correlation context after each test."""
    yield
    clear_correlation_context()
    # Reset structlog to a clean state so tests don't bleed into each other.
    structlog.reset_defaults()


@pytest.fixture()
def minimal_config() -> LoggingConfig:
    """Return a minimal LoggingConfig for testing (no file I/O)."""
    return LoggingConfig(
        level=LogLevel.DEBUG,
        format=LogFormat.CONSOLE,
        include_timestamp=False,
        include_caller=False,
        suppress_third_party=False,
        file=LogFileConfig(enabled=False),
    )


@pytest.fixture()
def logging_manager(minimal_config: LoggingConfig) -> LoggingManager:
    """Return an initialised LoggingManager with a minimal config."""
    manager = LoggingManager(config=minimal_config)
    manager.initialise()
    return manager


@pytest.fixture()
def factory(logging_manager: LoggingManager) -> LoggerFactory:
    """Return the LoggerFactory from the test LoggingManager."""
    return logging_manager.factory


# ---------------------------------------------------------------------------
# Correlation ID generation
# ---------------------------------------------------------------------------


@pytest.mark.unit()
class TestCorrelationProvider:
    """Tests for UUIDCorrelationProvider."""

    def test_generates_unique_correlation_ids(self) -> None:
        provider = UUIDCorrelationProvider()
        ids = {provider.generate_correlation_id() for _ in range(100)}
        assert len(ids) == 100

    def test_correlation_id_is_uuid_format(self) -> None:
        cid = generate_correlation_id()
        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        )
        assert uuid_pattern.match(cid), f"Not a valid UUID4: {cid}"

    def test_trace_id_is_32_hex_chars(self) -> None:
        tid = generate_trace_id()
        assert len(tid) == 32
        assert all(c in "0123456789abcdef" for c in tid)

    def test_generates_unique_trace_ids(self) -> None:
        provider = UUIDCorrelationProvider()
        ids = {provider.generate_trace_id() for _ in range(100)}
        assert len(ids) == 100

    def test_module_level_convenience_functions(self) -> None:
        cid = generate_correlation_id()
        tid = generate_trace_id()
        assert isinstance(cid, str) and len(cid) > 0
        assert isinstance(tid, str) and len(tid) == 32


# ---------------------------------------------------------------------------
# CorrelationContext model
# ---------------------------------------------------------------------------


@pytest.mark.unit()
class TestCorrelationContext:
    """Tests for the CorrelationContext dataclass."""

    def test_requires_correlation_id(self) -> None:
        ctx = CorrelationContext(correlation_id="abc-123")
        assert ctx.correlation_id == "abc-123"

    def test_all_optional_fields_default_to_none(self) -> None:
        ctx = CorrelationContext(correlation_id="x")
        assert ctx.trace_id is None
        assert ctx.pipeline_id is None
        assert ctx.stage_id is None
        assert ctx.execution_id is None
        assert ctx.command_name is None
        assert ctx.query_name is None
        assert ctx.event_name is None

    def test_with_pipeline_returns_new_instance(self) -> None:
        ctx = CorrelationContext(correlation_id="x")
        child = ctx.with_pipeline(pipeline_id="pipe-1", execution_id="exec-1")
        assert child is not ctx
        assert child.pipeline_id == "pipe-1"
        assert child.execution_id == "exec-1"
        assert child.correlation_id == "x"

    def test_with_stage_returns_new_instance(self) -> None:
        ctx = CorrelationContext(correlation_id="x")
        child = ctx.with_stage(stage_id="stage-1")
        assert child.stage_id == "stage-1"
        assert child.correlation_id == "x"

    def test_with_command_returns_new_instance(self) -> None:
        ctx = CorrelationContext(correlation_id="x")
        child = ctx.with_command(command_name="CreateDocumentCommand")
        assert child.command_name == "CreateDocumentCommand"

    def test_with_query_returns_new_instance(self) -> None:
        ctx = CorrelationContext(correlation_id="x")
        child = ctx.with_query(query_name="GetDocumentQuery")
        assert child.query_name == "GetDocumentQuery"

    def test_with_event_returns_new_instance(self) -> None:
        ctx = CorrelationContext(correlation_id="x")
        child = ctx.with_event(event_name="DocumentCreated")
        assert child.event_name == "DocumentCreated"

    def test_frozen_raises_on_mutation(self) -> None:
        ctx = CorrelationContext(correlation_id="x")
        with pytest.raises((AttributeError, TypeError)):
            ctx.correlation_id = "y"  # type: ignore[misc]

    def test_to_log_dict_only_includes_set_fields(self) -> None:
        ctx = CorrelationContext(correlation_id="x")
        d = ctx.to_log_dict()
        assert d == {"correlation_id": "x"}

    def test_to_log_dict_includes_all_set_fields(self) -> None:
        ctx = CorrelationContext(
            correlation_id="x",
            pipeline_id="pipe-1",
            stage_id="stage-1",
        )
        d = ctx.to_log_dict()
        assert d["correlation_id"] == "x"
        assert d["pipeline_id"] == "pipe-1"
        assert d["stage_id"] == "stage-1"
        assert "trace_id" not in d

    def test_context_is_immutable(self) -> None:
        ctx = CorrelationContext(correlation_id="x")
        original_pipeline = ctx.pipeline_id
        _ = ctx.with_pipeline(pipeline_id="new-pipe")
        assert ctx.pipeline_id == original_pipeline  # Original unchanged


# ---------------------------------------------------------------------------
# Context variable management
# ---------------------------------------------------------------------------


@pytest.mark.unit()
class TestContextVariable:
    """Tests for contextvars-based correlation context management."""

    def test_get_returns_none_before_set(self) -> None:
        clear_correlation_context()
        assert get_correlation_context() is None

    def test_set_and_get(self) -> None:
        ctx = CorrelationContext(correlation_id="test-id")
        set_correlation_context(ctx)
        result = get_correlation_context()
        assert result is not None
        assert result.correlation_id == "test-id"

    def test_clear_removes_context(self) -> None:
        ctx = CorrelationContext(correlation_id="test-id")
        set_correlation_context(ctx)
        clear_correlation_context()
        assert get_correlation_context() is None

    def test_reset_restores_previous(self) -> None:
        ctx1 = CorrelationContext(correlation_id="first")
        ctx2 = CorrelationContext(correlation_id="second")

        set_correlation_context(ctx1)
        token = set_correlation_context(ctx2)
        assert get_correlation_context().correlation_id == "second"  # type: ignore[union-attr]

        from infrastructure.logging.context import reset_correlation_context
        reset_correlation_context(token)
        # After reset the token points back to ctx1
        assert get_correlation_context() is not None


# ---------------------------------------------------------------------------
# ExceptionInfo
# ---------------------------------------------------------------------------


@pytest.mark.unit()
class TestExceptionInfo:
    """Tests for ExceptionInfo structured exception capture."""

    def test_from_exception_captures_type(self) -> None:
        try:
            raise ValueError("something went wrong")
        except ValueError as exc:
            info = ExceptionInfo.from_exception(exc)
        assert info.exc_type == "ValueError"

    def test_from_exception_captures_message(self) -> None:
        try:
            raise RuntimeError("test error message")
        except RuntimeError as exc:
            info = ExceptionInfo.from_exception(exc)
        assert info.message == "test error message"

    def test_from_exception_captures_traceback(self) -> None:
        try:
            raise TypeError("type problem")
        except TypeError as exc:
            info = ExceptionInfo.from_exception(exc)
        assert "TypeError" in info.traceback
        assert "type problem" in info.traceback

    def test_to_dict_contains_required_keys(self) -> None:
        try:
            raise ValueError("x")
        except ValueError as exc:
            d = ExceptionInfo.from_exception(exc).to_dict()
        assert set(d.keys()) == {"exc_type", "message", "traceback"}


# ---------------------------------------------------------------------------
# LogEntry model
# ---------------------------------------------------------------------------


@pytest.mark.unit()
class TestLogEntry:
    """Tests for the LogEntry dataclass."""

    def test_default_timestamp_is_utc(self) -> None:
        from datetime import timezone
        entry = LogEntry(event="test")
        assert entry.timestamp.tzinfo == timezone.utc

    def test_to_dict_contains_required_keys(self) -> None:
        entry = LogEntry(event="test_event", level="INFO")
        d = entry.to_dict()
        assert "timestamp" in d
        assert "level" in d
        assert "event" in d
        assert d["event"] == "test_event"

    def test_to_dict_omits_none_fields(self) -> None:
        entry = LogEntry(event="test_event")
        d = entry.to_dict()
        assert "pipeline_id" not in d
        assert "trace_id" not in d

    def test_to_dict_includes_exception(self) -> None:
        try:
            raise ValueError("oops")
        except ValueError as exc:
            exc_info = ExceptionInfo.from_exception(exc)
        entry = LogEntry(event="failed", exception=exc_info)
        d = entry.to_dict()
        assert "exception" in d
        assert d["exception"]["exc_type"] == "ValueError"


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------


@pytest.mark.unit()
class TestFormatters:
    """Tests for ConsoleFormatter and JSONFormatter."""

    def test_console_formatter_format_id(self) -> None:
        assert ConsoleFormatter().format_id == "console"

    def test_json_formatter_format_id(self) -> None:
        assert JSONFormatter().format_id == "json"

    def test_console_formatter_builds_processors(self) -> None:
        procs = ConsoleFormatter().build_processors()
        assert isinstance(procs, list)
        assert len(procs) > 0

    def test_json_formatter_builds_processors(self) -> None:
        procs = JSONFormatter().build_processors()
        assert isinstance(procs, list)
        assert len(procs) > 0

    def test_build_formatter_console(self) -> None:
        f = build_formatter("console")
        assert f.format_id == "console"

    def test_build_formatter_json(self) -> None:
        f = build_formatter("json")
        assert f.format_id == "json"

    def test_build_formatter_unknown_raises(self) -> None:
        with pytest.raises(FormatterNotFoundError):
            build_formatter("unknown_format")


# ---------------------------------------------------------------------------
# Log level filter
# ---------------------------------------------------------------------------


@pytest.mark.unit()
class TestLogLevelFilter:
    """Tests for the LogLevelFilter structlog processor."""

    def test_passes_at_minimum_level(self) -> None:
        f = LogLevelFilter(min_level="info")
        result = f(None, "info", {"event": "x"})
        assert result["event"] == "x"

    def test_passes_above_minimum_level(self) -> None:
        f = LogLevelFilter(min_level="info")
        result = f(None, "warning", {"event": "x"})
        assert result["event"] == "x"

    def test_drops_below_minimum_level(self) -> None:
        import structlog

        f = LogLevelFilter(min_level="warning")
        with pytest.raises(structlog.DropEvent):
            f(None, "debug", {"event": "x"})

    def test_case_insensitive_level(self) -> None:
        f = LogLevelFilter(min_level="INFO")
        result = f(None, "INFO", {"event": "x"})
        assert result is not None


# ---------------------------------------------------------------------------
# Sensitive data filter
# ---------------------------------------------------------------------------


@pytest.mark.unit()
class TestSensitiveDataFilter:
    """Tests for the SensitiveDataFilter structlog processor."""

    def test_redacts_password_field(self) -> None:
        f = SensitiveDataFilter()
        result = f(None, "info", {"event": "login", "password": "secret123"})
        assert result["password"] == "[REDACTED]"

    def test_redacts_token_field(self) -> None:
        f = SensitiveDataFilter()
        result = f(None, "info", {"event": "auth", "token": "abc.def.ghi"})
        assert result["token"] == "[REDACTED]"

    def test_leaves_non_sensitive_fields_intact(self) -> None:
        f = SensitiveDataFilter()
        result = f(None, "info", {"event": "action", "user_id": "123", "action": "read"})
        assert result["user_id"] == "123"
        assert result["action"] == "read"

    def test_event_not_redacted(self) -> None:
        f = SensitiveDataFilter()
        result = f(None, "info", {"event": "something"})
        assert result["event"] == "something"


# ---------------------------------------------------------------------------
# LoggingManager
# ---------------------------------------------------------------------------


@pytest.mark.unit()
class TestLoggingManager:
    """Tests for LoggingManager initialisation and access."""

    def test_is_not_initialised_before_init(self, minimal_config: LoggingConfig) -> None:
        manager = LoggingManager(config=minimal_config)
        assert manager.is_initialised is False

    def test_is_initialised_after_init(self, logging_manager: LoggingManager) -> None:
        assert logging_manager.is_initialised is True

    def test_initialise_is_idempotent(self, minimal_config: LoggingConfig) -> None:
        manager = LoggingManager(config=minimal_config)
        manager.initialise()
        manager.initialise()  # Second call — must not raise
        assert manager.is_initialised is True

    def test_factory_raises_before_init(self, minimal_config: LoggingConfig) -> None:
        manager = LoggingManager(config=minimal_config)
        with pytest.raises(LoggingNotInitialisedError):
            _ = manager.factory

    def test_factory_available_after_init(self, logging_manager: LoggingManager) -> None:
        assert isinstance(logging_manager.factory, LoggerFactory)

    def test_config_property(self, logging_manager: LoggingManager) -> None:
        assert logging_manager.config.format == LogFormat.CONSOLE

    def test_shutdown_does_not_raise(self, logging_manager: LoggingManager) -> None:
        logging_manager.shutdown()  # Must not raise
        assert logging_manager.is_initialised is False

    def test_json_format_config(self) -> None:
        config = LoggingConfig(
            level=LogLevel.INFO,
            format=LogFormat.JSON,
            file=LogFileConfig(enabled=False),
        )
        manager = LoggingManager(config=config)
        manager.initialise()
        assert manager.is_initialised
        manager.shutdown()

    def test_log_level_warning_suppresses_debug(self) -> None:
        config = LoggingConfig(
            level=LogLevel.WARNING,
            format=LogFormat.CONSOLE,
            file=LogFileConfig(enabled=False),
        )
        manager = LoggingManager(config=config)
        manager.initialise()
        root = logging.getLogger()
        assert root.level == logging.WARNING
        manager.shutdown()

    def test_shutdown_removes_handlers_from_root_logger(self) -> None:
        """Handlers must be removed from the root logger on shutdown.

        Re-initialising after shutdown should not stack duplicate handlers.
        """
        config = LoggingConfig(
            level=LogLevel.DEBUG,
            format=LogFormat.CONSOLE,
            file=LogFileConfig(enabled=False),
        )
        root = logging.getLogger()
        handlers_before = len(root.handlers)

        manager = LoggingManager(config=config)
        manager.initialise()
        handlers_after_init = len(root.handlers)
        assert handlers_after_init > handlers_before  # handlers were added

        manager.shutdown()
        handlers_after_shutdown = len(root.handlers)
        assert handlers_after_shutdown == handlers_before  # handlers were removed

    def test_reinitialise_after_shutdown_does_not_duplicate_handlers(self) -> None:
        """Init → shutdown → init must not double the handler count."""
        config = LoggingConfig(
            level=LogLevel.DEBUG,
            format=LogFormat.CONSOLE,
            file=LogFileConfig(enabled=False),
        )
        root = logging.getLogger()

        m1 = LoggingManager(config=config)
        m1.initialise()
        count_first = len(root.handlers)
        m1.shutdown()

        m2 = LoggingManager(config=config)
        m2.initialise()
        count_second = len(root.handlers)
        m2.shutdown()

        assert count_second == count_first  # no duplicates

    def test_include_timestamp_false_omits_timestamper(self) -> None:
        """When include_timestamp=False, no timestamp field should appear in log records."""
        import io

        config = LoggingConfig(
            level=LogLevel.DEBUG,
            format=LogFormat.CONSOLE,
            include_timestamp=False,
            include_caller=False,
            suppress_third_party=False,
            file=LogFileConfig(enabled=False),
        )
        manager = LoggingManager(config=config)
        manager.initialise()

        # Inspect the processor chain: TimeStamper must not be present.
        # We verify indirectly by checking the shared processor list built
        # by the manager does not include a TimeStamper when disabled.
        processors = manager._build_shared_processors()
        has_timestamper = any(
            isinstance(p, structlog.processors.TimeStamper) for p in processors
        )
        assert not has_timestamper, "TimeStamper should not be in the chain when include_timestamp=False"
        manager.shutdown()

    def test_include_timestamp_true_includes_timestamper(self) -> None:
        """When include_timestamp=True, the TimeStamper processor must be present."""
        config = LoggingConfig(
            level=LogLevel.DEBUG,
            format=LogFormat.CONSOLE,
            include_timestamp=True,
            include_caller=False,
            suppress_third_party=False,
            file=LogFileConfig(enabled=False),
        )
        manager = LoggingManager(config=config)
        processors = manager._build_shared_processors()
        has_timestamper = any(
            isinstance(p, structlog.processors.TimeStamper) for p in processors
        )
        assert has_timestamper, "TimeStamper should be in the chain when include_timestamp=True"


# ---------------------------------------------------------------------------
# LoggerFactory
# ---------------------------------------------------------------------------


@pytest.mark.unit()
class TestLoggerFactory:
    """Tests for LoggerFactory logger creation."""

    def test_returns_rkgb_logger(self, factory: LoggerFactory) -> None:
        logger = factory.get_logger("test.component")
        assert isinstance(logger, RKGBLogger)

    def test_component_name_is_set(self, factory: LoggerFactory) -> None:
        logger = factory.get_logger("my.service")
        assert logger.component == "my.service"

    def test_bound_context_is_passed(self, factory: LoggerFactory) -> None:
        logger = factory.get_logger("svc", request_id="req-1")
        assert isinstance(logger, RKGBLogger)

    def test_with_extra_creates_new_factory(self, factory: LoggerFactory) -> None:
        new_factory = factory.with_extra(app_version="1.0.0")
        assert new_factory is not factory

    def test_factory_loggers_are_independent(self, factory: LoggerFactory) -> None:
        a = factory.get_logger("component.a")
        b = factory.get_logger("component.b")
        assert a.component == "component.a"
        assert b.component == "component.b"


# ---------------------------------------------------------------------------
# RKGBLogger
# ---------------------------------------------------------------------------


@pytest.mark.unit()
class TestRKGBLogger:
    """Tests for RKGBLogger log emission and binding."""

    def test_bind_returns_new_logger(self, factory: LoggerFactory) -> None:
        logger = factory.get_logger("svc")
        bound = logger.bind(request_id="abc")
        assert bound is not logger
        assert isinstance(bound, RKGBLogger)

    def test_unbind_returns_new_logger(self, factory: LoggerFactory) -> None:
        logger = factory.get_logger("svc").bind(request_id="abc")
        unbound = logger.unbind("request_id")
        assert isinstance(unbound, RKGBLogger)

    def test_log_methods_do_not_raise(self, factory: LoggerFactory) -> None:
        logger = factory.get_logger("test")
        logger.debug("debug_event")
        logger.info("info_event")
        logger.warning("warning_event")
        logger.error("error_event")
        logger.critical("critical_event")

    def test_exception_logging_does_not_raise(self, factory: LoggerFactory) -> None:
        logger = factory.get_logger("test")
        try:
            raise ValueError("test exception")
        except ValueError:
            logger.exception("caught_exception")  # Must not raise

    def test_log_command_dispatched(self, factory: LoggerFactory) -> None:
        logger = factory.get_logger("command_bus")
        logger.log_command_dispatched("CreateDocumentCommand")  # Must not raise

    def test_log_command_completed(self, factory: LoggerFactory) -> None:
        logger = factory.get_logger("command_bus")
        logger.log_command_completed("CreateDocumentCommand", duration_ms=12.5)

    def test_log_command_failed(self, factory: LoggerFactory) -> None:
        logger = factory.get_logger("command_bus")
        exc = RuntimeError("handler failed")
        logger.log_command_failed("CreateDocumentCommand", exc, duration_ms=5.0)

    def test_log_query_dispatched(self, factory: LoggerFactory) -> None:
        logger = factory.get_logger("query_bus")
        logger.log_query_dispatched("GetDocumentQuery")

    def test_log_event_published(self, factory: LoggerFactory) -> None:
        logger = factory.get_logger("event_bus")
        logger.log_event_published("DocumentCreated")

    def test_log_pipeline_stage_started(self, factory: LoggerFactory) -> None:
        logger = factory.get_logger("pipeline")
        logger.log_pipeline_stage_started("extraction_stage")

    def test_log_pipeline_stage_completed(self, factory: LoggerFactory) -> None:
        logger = factory.get_logger("pipeline")
        logger.log_pipeline_stage_completed("extraction_stage", duration_ms=250.0)

    def test_log_pipeline_stage_failed(self, factory: LoggerFactory) -> None:
        logger = factory.get_logger("pipeline")
        exc = IOError("disk full")
        logger.log_pipeline_stage_failed("extraction_stage", exc, duration_ms=10.0)


# ---------------------------------------------------------------------------
# build_test_logging_manager convenience function
# ---------------------------------------------------------------------------


@pytest.mark.unit()
class TestBuildTestLoggingManager:
    """Tests for the build_test_logging_manager bootstrap helper."""

    def test_returns_initialised_manager(self) -> None:
        manager = build_test_logging_manager()
        assert manager.is_initialised

    def test_factory_is_available(self) -> None:
        manager = build_test_logging_manager()
        assert isinstance(manager.factory, LoggerFactory)

    def test_accepts_overrides(self) -> None:
        manager = build_test_logging_manager({"level": LogLevel.WARNING})
        assert manager.config.level == LogLevel.WARNING

    def test_cleanup(self) -> None:
        manager = build_test_logging_manager()
        manager.shutdown()
        assert not manager.is_initialised
