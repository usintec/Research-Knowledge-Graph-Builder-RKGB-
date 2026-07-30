"""Abstract interfaces for the RKGB Logging & Observability Framework.

All logging components depend on these interfaces rather than on concrete
implementations — following the Dependency Inversion Principle.

Design note: A mix of ABCs and ``typing.Protocol`` is used deliberately:
- ABCs for stateful components that carry configuration (handlers, formatters)
  so that subclass contract is enforced at class-definition time.
- Protocols for pure behavioural contracts consumed by business-layer code
  (``ILogger``, ``ICorrelationProvider``) so that any duck-typed object that
  satisfies the interface can be used without inheriting from RKGB base classes.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from infrastructure.logging.models.context import CorrelationContext


# ---------------------------------------------------------------------------
# Logger protocol — consumed by business code
# ---------------------------------------------------------------------------


@runtime_checkable
class ILogger(Protocol):
    """Structural interface for all RKGB loggers.

    Business code depends on this protocol so it is not coupled to the
    concrete ``RKGBLogger`` or any specific structlog type.

    Example::

        class MyService:
            def __init__(self, logger: ILogger) -> None:
                self._log = logger

            def do_work(self) -> None:
                self._log.info("doing_work", extra_field="value")
    """

    def debug(self, event: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Emit a DEBUG-level log entry."""
        ...

    def info(self, event: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Emit an INFO-level log entry."""
        ...

    def warning(self, event: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Emit a WARNING-level log entry."""
        ...

    def error(self, event: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Emit an ERROR-level log entry."""
        ...

    def critical(self, event: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Emit a CRITICAL-level log entry."""
        ...

    def bind(self, **new_values: Any) -> "ILogger":  # noqa: ANN401
        """Return a new logger with additional bound context fields.

        Args:
            **new_values: Key-value pairs to bind into every subsequent log entry.

        Returns:
            A new ``ILogger`` instance with the additional context.
        """
        ...


# ---------------------------------------------------------------------------
# Log handler ABC — stateful, carries configuration
# ---------------------------------------------------------------------------


class ILogHandler(ABC):
    """Abstract base for RKGB log handlers.

    Each handler wraps a ``logging.Handler`` from the standard library so
    that the framework integrates cleanly with structlog's stdlib sink.

    Args:
        handler_id: Unique identifier for this handler instance.
    """

    def __init__(self, handler_id: str) -> None:
        self._handler_id = handler_id

    @property
    def handler_id(self) -> str:
        """Unique identifier for this handler.

        Returns:
            Handler identifier string.
        """
        return self._handler_id

    @abstractmethod
    def build(self) -> logging.Handler:
        """Construct and return the underlying ``logging.Handler``.

        Returns:
            Configured :class:`logging.Handler` ready to be attached to the
            root logger.
        """

    def is_available(self) -> bool:
        """Return ``True`` if this handler can be used in the current environment.

        Subclasses may override to check file-system permissions, network
        reachability, etc.

        Returns:
            ``True`` by default.
        """
        return True


# ---------------------------------------------------------------------------
# Log formatter ABC
# ---------------------------------------------------------------------------


class ILogFormatter(ABC):
    """Abstract base for RKGB log formatters.

    A formatter converts a structlog event dictionary into a final string
    representation consumed by handlers.
    """

    @property
    @abstractmethod
    def format_id(self) -> str:
        """Unique identifier for this formatter (e.g. ``"console"``, ``"json"``).

        Returns:
            Format identifier string.
        """

    @abstractmethod
    def build_processors(self) -> list[Any]:  # noqa: ANN401
        """Return the ordered list of structlog processors for this format.

        The returned list is appended to the shared processor chain.

        Returns:
            List of callables (structlog processors).
        """


# ---------------------------------------------------------------------------
# Log filter ABC
# ---------------------------------------------------------------------------


class ILogFilter(ABC):
    """Abstract base for RKGB log filters.

    Filters are applied in the structlog processor chain; they can suppress,
    enrich, or transform log records before they reach the handler.
    """

    @abstractmethod
    def __call__(
        self,
        logger: Any,  # noqa: ANN401
        method: str,
        event_dict: dict[str, Any],  # noqa: ANN401
    ) -> dict[str, Any]:  # noqa: ANN401
        """Process a structlog event dict.

        Args:
            logger: The bound structlog logger (may be ``None``).
            method: The log level method name (e.g. ``"info"``, ``"error"``).
            event_dict: Mutable event dictionary to transform.

        Returns:
            The (possibly modified) event dictionary.

        Raises:
            structlog.DropEvent: To suppress the log entry entirely.
        """


# ---------------------------------------------------------------------------
# Correlation provider protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class ICorrelationProvider(Protocol):
    """Structural interface for correlation ID generation.

    Implementations must produce unique, URL-safe string identifiers suitable
    for distributed tracing.
    """

    def generate_correlation_id(self) -> str:
        """Generate a new correlation ID.

        Returns:
            Unique string identifier.
        """
        ...

    def generate_trace_id(self) -> str:
        """Generate a new trace ID.

        Returns:
            Unique string identifier compatible with OpenTelemetry trace IDs.
        """
        ...


# ---------------------------------------------------------------------------
# Metrics hook protocol (future — for OpenTelemetry / Prometheus integration)
# ---------------------------------------------------------------------------


@runtime_checkable
class IMetricsEmitter(Protocol):
    """Structural interface for emitting metrics from log events.

    Logging events that carry timing or counter information will call this
    protocol so that, when a metrics backend is wired up (Prometheus, OTEL),
    metrics can be emitted without modifying the logging framework.

    This protocol is intentionally minimal — the concrete implementation
    decides which events increment counters, record timings, etc.
    """

    def increment(self, metric: str, *, labels: dict[str, str] | None = None) -> None:
        """Increment a counter metric.

        Args:
            metric: Metric name.
            labels: Optional label key-value pairs.
        """
        ...

    def record_duration(
        self,
        metric: str,
        duration_ms: float,
        *,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a duration observation (histogram/timer).

        Args:
            metric: Metric name.
            duration_ms: Duration in milliseconds.
            labels: Optional label key-value pairs.
        """
        ...
