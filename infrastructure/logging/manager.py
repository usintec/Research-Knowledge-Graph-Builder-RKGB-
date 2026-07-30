"""Logging Manager — the central orchestrator for the logging framework.

``LoggingManager`` is the single authority for configuring structlog and the
Python standard ``logging`` module.  It:

* Configures structlog's global processor chain.
* Creates and attaches handlers to the root stdlib logger.
* Applies log-level suppression for third-party libraries.
* Exposes the :class:`~infrastructure.logging.factory.LoggerFactory` for DI.

**Only one instance should exist per application process.**  The DI container
(Step A4) is responsible for enforcing this by binding ``LoggingManager`` as a
singleton.

Integration with the DI container (preview — implemented in Step A4)::

    manager = bootstrap_logging(config_manager)
    container.define(LoggingManager, lambda: manager)
    container.define(LoggerFactory, lambda: manager.factory)
"""

from __future__ import annotations

import logging

import structlog

from infrastructure.config.models.logging import LogFormat, LogLevel, LoggingConfig
from infrastructure.logging.constants import (
    MSG_LOGGING_INITIALISED,
    MSG_LOGGING_SHUTDOWN,
    THIRD_PARTY_LOGGERS,
)
from infrastructure.logging.exceptions import LoggingNotInitialisedError
from infrastructure.logging.factory import LoggerFactory
from infrastructure.logging.filters import SensitiveDataFilter, ThirdPartySuppressionFilter
from infrastructure.logging.formatter import ConsoleFormatter, JSONFormatter
from infrastructure.logging.handlers import (
    ConsoleLogHandler,
    RotatingFileLogHandler,
)


_LEVEL_MAP: dict[LogLevel, int] = {
    LogLevel.DEBUG: logging.DEBUG,
    LogLevel.INFO: logging.INFO,
    LogLevel.WARNING: logging.WARNING,
    LogLevel.ERROR: logging.ERROR,
    LogLevel.CRITICAL: logging.CRITICAL,
}


class LoggingManager:
    """Central manager for the RKGB Logging & Observability Framework.

    Configures structlog, stdlib root logger, handlers, and formatters
    from a :class:`~infrastructure.config.models.logging.LoggingConfig`
    instance.

    Args:
        config: Resolved logging configuration.
    """

    def __init__(self, config: LoggingConfig) -> None:
        self._config = config
        self._factory: LoggerFactory | None = None
        self._initialised = False
        self._stdlib_handlers: list[logging.Handler] = []

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialise(self) -> None:
        """Configure structlog and the stdlib root logger.

        This method is idempotent — calling it multiple times has no effect
        after the first successful call.

        Called by :func:`~infrastructure.logging.bootstrap.bootstrap_logging`
        during application startup.
        """
        if self._initialised:
            return

        numeric_level = _LEVEL_MAP[self._config.level]

        # 1. Build the shared pre-processor chain (runs before the renderer).
        shared_processors = self._build_shared_processors()

        # 2. Configure structlog globally.
        structlog.configure(
            processors=[
                *shared_processors,
                # The stdlib renderer hands off to the stdlib logging system.
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            cache_logger_on_first_use=True,
        )

        # 3. Build and attach handlers to the stdlib root logger.
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)

        for handler in self._build_handlers(numeric_level):
            root_logger.addHandler(handler)
            self._stdlib_handlers.append(handler)

        # 4. Suppress noisy third-party loggers.
        if self._config.suppress_third_party:
            self._suppress_third_party(numeric_level)

        # 5. Build the logger factory.
        self._factory = LoggerFactory()

        self._initialised = True

        # Emit the initialisation event using the factory.
        self._factory.get_logger("rkgb.logging").info(
            MSG_LOGGING_INITIALISED,
            log_level=self._config.level.value,
            log_format=self._config.format.value,
            file_logging=self._config.file.enabled,
        )

    def shutdown(self) -> None:
        """Flush, close, and remove all managed handlers from the root logger.

        Should be called during application shutdown to ensure all buffered
        log records are written.  Also removes each handler from the stdlib
        root logger so that re-initialising (e.g. in tests or app reloads)
        does not stack duplicate handlers.
        """
        if self._factory and self._initialised:
            self._factory.get_logger("rkgb.logging").info(MSG_LOGGING_SHUTDOWN)

        root_logger = logging.getLogger()
        for handler in self._stdlib_handlers:
            try:
                root_logger.removeHandler(handler)
                handler.flush()
                handler.close()
            except Exception:  # noqa: BLE001
                pass  # Never let logging teardown crash the application.

        self._stdlib_handlers.clear()
        self._initialised = False

    # ------------------------------------------------------------------
    # Access
    # ------------------------------------------------------------------

    @property
    def factory(self) -> LoggerFactory:
        """Return the :class:`~infrastructure.logging.factory.LoggerFactory`.

        Returns:
            The singleton :class:`LoggerFactory` for this manager.

        Raises:
            :class:`~infrastructure.logging.exceptions.LoggingNotInitialisedError`:
                If :meth:`initialise` has not been called.
        """
        if self._factory is None:
            raise LoggingNotInitialisedError()
        return self._factory

    @property
    def is_initialised(self) -> bool:
        """Return ``True`` if the framework has been initialised.

        Returns:
            ``bool``.
        """
        return self._initialised

    @property
    def config(self) -> LoggingConfig:
        """Return the active logging configuration.

        Returns:
            :class:`~infrastructure.config.models.logging.LoggingConfig`.
        """
        return self._config

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_shared_processors(self) -> list[object]:
        """Build the processor chain that runs on every log event.

        Returns:
            Ordered list of structlog processors.
        """
        processors: list[object] = [
            # Merge context-var fields (correlation IDs, etc.) into event dict.
            structlog.contextvars.merge_contextvars,
            # Inject Python stdlib log level info.
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
        ]

        # Only add timestamp when the configuration requests it.
        if self._config.include_timestamp:
            processors.append(structlog.processors.TimeStamper(fmt="iso", utc=True))

        # Render stack info from exc_info= kwarg.
        processors.append(structlog.processors.StackInfoRenderer())

        if self._config.include_caller:
            processors.append(
                structlog.processors.CallsiteParameterAdder(
                    [
                        structlog.processors.CallsiteParameter.FILENAME,
                        structlog.processors.CallsiteParameter.LINENO,
                    ]
                )
            )

        # Sensitive-data redaction — always active.
        processors.append(SensitiveDataFilter())

        # Third-party suppression in the processor chain.
        if self._config.suppress_third_party:
            processors.append(ThirdPartySuppressionFilter())

        return processors

    def _build_handlers(self, numeric_level: int) -> list[logging.Handler]:
        """Create all configured log handlers.

        Args:
            numeric_level: Numeric log level from stdlib constants.

        Returns:
            List of configured :class:`logging.Handler` instances.
        """
        handlers: list[logging.Handler] = []

        # Always add a console handler.
        formatter = self._pick_formatter()
        console = ConsoleLogHandler(formatter=formatter, level=numeric_level)
        if console.is_available():
            handlers.append(console.build())

        # Optional file handler.
        if self._config.file.enabled and self._config.log_file_path:
            rotating = RotatingFileLogHandler(
                path=self._config.log_file_path,
                formatter=formatter,
                max_bytes=self._config.file.max_bytes,
                backup_count=self._config.file.backup_count,
                level=numeric_level,
            )
            if rotating.is_available():
                handlers.append(rotating.build())

        return handlers

    def _pick_formatter(self) -> ConsoleFormatter | JSONFormatter:
        """Return the formatter appropriate for the configured format.

        Returns:
            :class:`~infrastructure.logging.formatter.ConsoleFormatter` or
            :class:`~infrastructure.logging.formatter.JSONFormatter`.
        """
        if self._config.format == LogFormat.JSON:
            return JSONFormatter(
                include_timestamp=self._config.include_timestamp,
                include_caller=self._config.include_caller,
            )
        return ConsoleFormatter(
            include_timestamp=self._config.include_timestamp,
            include_caller=self._config.include_caller,
        )

    def _suppress_third_party(self, app_level: int) -> None:
        """Raise third-party loggers to WARNING or higher.

        Args:
            app_level: The application's numeric log level.
        """
        suppress_level = max(app_level, logging.WARNING)
        for name in THIRD_PARTY_LOGGERS:
            logging.getLogger(name).setLevel(suppress_level)
