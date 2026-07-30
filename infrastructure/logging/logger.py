"""RKGB logger wrapper around structlog's bound logger.

:class:`RKGBLogger` is the concrete logger returned by the
:class:`~infrastructure.logging.factory.LoggerFactory`.  It wraps a structlog
``BoundLoggerLazyProxy`` and satisfies the :class:`~infrastructure.logging.interfaces.ILogger`
protocol so business code can depend on the protocol rather than this class.

Usage::

    from infrastructure.logging.factory import LoggerFactory

    # Obtained via DI — never constructed directly:
    logger = factory.get_logger("my_service")
    logger.info("entity_created", entity_id="abc-123")
    logger.error("operation_failed", exc_info=True)

    # Add context for a scoped operation:
    scoped = logger.bind(request_id="req-999")
    scoped.info("processing_started")
"""

from __future__ import annotations

from typing import Any

import structlog


class RKGBLogger:
    """Structured logger wrapping a structlog bound logger.

    Satisfies :class:`~infrastructure.logging.interfaces.ILogger` via duck
    typing so it can be used wherever that protocol is expected.

    Args:
        bound_logger: Pre-configured structlog bound logger instance.
        component: Component name embedded in every log entry.
    """

    def __init__(
        self,
        bound_logger: Any,  # noqa: ANN401  # structlog types are complex
        component: str,
    ) -> None:
        self._logger = bound_logger
        self._component = component

    # ------------------------------------------------------------------
    # Core logging methods (ILogger protocol)
    # ------------------------------------------------------------------

    def debug(self, event: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Emit a DEBUG-level log entry.

        Args:
            event: Human-readable event description or slug.
            **kwargs: Additional structured key-value context fields.
        """
        self._logger.debug(event, component=self._component, **kwargs)

    def info(self, event: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Emit an INFO-level log entry.

        Args:
            event: Human-readable event description or slug.
            **kwargs: Additional structured key-value context fields.
        """
        self._logger.info(event, component=self._component, **kwargs)

    def warning(self, event: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Emit a WARNING-level log entry.

        Args:
            event: Human-readable event description or slug.
            **kwargs: Additional structured key-value context fields.
        """
        self._logger.warning(event, component=self._component, **kwargs)

    def error(self, event: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Emit an ERROR-level log entry.

        Args:
            event: Human-readable event description or slug.
            **kwargs: Additional structured key-value context fields.
        """
        self._logger.error(event, component=self._component, **kwargs)

    def critical(self, event: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Emit a CRITICAL-level log entry.

        Args:
            event: Human-readable event description or slug.
            **kwargs: Additional structured key-value context fields.
        """
        self._logger.critical(event, component=self._component, **kwargs)

    def exception(self, event: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Emit an ERROR-level log entry with full exception traceback.

        Should be called from an active ``except`` block.

        Args:
            event: Human-readable event description or slug.
            **kwargs: Additional structured key-value context fields.
        """
        self._logger.exception(event, component=self._component, **kwargs)

    # ------------------------------------------------------------------
    # Context binding
    # ------------------------------------------------------------------

    def bind(self, **new_values: Any) -> "RKGBLogger":  # noqa: ANN401
        """Return a new logger with additional bound context fields.

        The returned logger shares the component name but carries the extra
        context in every subsequent log call.

        Args:
            **new_values: Key-value pairs to bind.

        Returns:
            New :class:`RKGBLogger` with the extended context.
        """
        return RKGBLogger(
            bound_logger=self._logger.bind(**new_values),
            component=self._component,
        )

    def unbind(self, *keys: str) -> "RKGBLogger":
        """Return a new logger with specified context fields removed.

        Args:
            *keys: Field names to remove from the bound context.

        Returns:
            New :class:`RKGBLogger` without the specified fields.
        """
        return RKGBLogger(
            bound_logger=self._logger.unbind(*keys),
            component=self._component,
        )

    # ------------------------------------------------------------------
    # Convenience: domain event / bus logging
    # ------------------------------------------------------------------

    def log_command_dispatched(
        self,
        command_name: str,
        *,
        correlation_id: str | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Log that a command has been dispatched to the command bus.

        Intended for use inside the Command Bus implementation (future step).

        Args:
            command_name: Fully-qualified command class name.
            correlation_id: Optional override for the correlation ID.
            **kwargs: Additional context fields.
        """
        self.info(
            "command_dispatched",
            command_name=command_name,
            **({"correlation_id": correlation_id} if correlation_id else {}),
            **kwargs,
        )

    def log_command_completed(
        self,
        command_name: str,
        *,
        duration_ms: float | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Log successful command handler completion.

        Args:
            command_name: Fully-qualified command class name.
            duration_ms: Execution duration in milliseconds.
            **kwargs: Additional context fields.
        """
        self.info(
            "command_completed",
            command_name=command_name,
            **({"duration_ms": duration_ms} if duration_ms is not None else {}),
            **kwargs,
        )

    def log_command_failed(
        self,
        command_name: str,
        exc: BaseException,
        *,
        duration_ms: float | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Log a command handler failure with exception details.

        Args:
            command_name: Fully-qualified command class name.
            exc: The exception that caused the failure.
            duration_ms: Execution duration in milliseconds.
            **kwargs: Additional context fields.
        """
        from infrastructure.logging.models.log_entry import ExceptionInfo

        self.error(
            "command_failed",
            command_name=command_name,
            exception=ExceptionInfo.from_exception(exc).to_dict(),
            **({"duration_ms": duration_ms} if duration_ms is not None else {}),
            **kwargs,
        )

    def log_query_dispatched(self, query_name: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Log that a query has been dispatched.

        Args:
            query_name: Fully-qualified query class name.
            **kwargs: Additional context fields.
        """
        self.info("query_dispatched", query_name=query_name, **kwargs)

    def log_query_completed(
        self,
        query_name: str,
        *,
        duration_ms: float | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Log successful query handler completion.

        Args:
            query_name: Fully-qualified query class name.
            duration_ms: Execution duration in milliseconds.
            **kwargs: Additional context fields.
        """
        self.info(
            "query_completed",
            query_name=query_name,
            **({"duration_ms": duration_ms} if duration_ms is not None else {}),
            **kwargs,
        )

    def log_event_published(self, event_name: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Log that a domain event has been published to the event bus.

        Args:
            event_name: Fully-qualified event class name.
            **kwargs: Additional context fields.
        """
        self.info("event_published", event_name=event_name, **kwargs)

    def log_event_subscriber_invoked(
        self, event_name: str, subscriber: str, **kwargs: Any  # noqa: ANN401
    ) -> None:
        """Log that an event subscriber has been invoked.

        Args:
            event_name: Fully-qualified event class name.
            subscriber: Subscriber handler name.
            **kwargs: Additional context fields.
        """
        self.debug(
            "event_subscriber_invoked",
            event_name=event_name,
            subscriber=subscriber,
            **kwargs,
        )

    def log_event_subscriber_completed(
        self,
        event_name: str,
        subscriber: str,
        *,
        duration_ms: float | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Log successful event subscriber completion.

        Args:
            event_name: Fully-qualified event class name.
            subscriber: Subscriber handler name.
            duration_ms: Execution duration in milliseconds.
            **kwargs: Additional context fields.
        """
        self.info(
            "event_subscriber_completed",
            event_name=event_name,
            subscriber=subscriber,
            **({"duration_ms": duration_ms} if duration_ms is not None else {}),
            **kwargs,
        )

    def log_pipeline_stage_started(self, stage_id: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Log that a pipeline stage has started.

        Args:
            stage_id: Stage identifier.
            **kwargs: Additional context fields.
        """
        self.info("pipeline_stage_started", stage_id=stage_id, **kwargs)

    def log_pipeline_stage_completed(
        self,
        stage_id: str,
        *,
        duration_ms: float | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Log that a pipeline stage has completed successfully.

        Args:
            stage_id: Stage identifier.
            duration_ms: Stage execution duration in milliseconds.
            **kwargs: Additional context fields.
        """
        self.info(
            "pipeline_stage_completed",
            stage_id=stage_id,
            **({"duration_ms": duration_ms} if duration_ms is not None else {}),
            **kwargs,
        )

    def log_pipeline_stage_failed(
        self,
        stage_id: str,
        exc: BaseException,
        *,
        duration_ms: float | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Log a pipeline stage failure with exception details.

        Args:
            stage_id: Stage identifier.
            exc: The exception that caused the failure.
            duration_ms: Stage execution duration in milliseconds.
            **kwargs: Additional context fields.
        """
        from infrastructure.logging.models.log_entry import ExceptionInfo

        self.error(
            "pipeline_stage_failed",
            stage_id=stage_id,
            exception=ExceptionInfo.from_exception(exc).to_dict(),
            **({"duration_ms": duration_ms} if duration_ms is not None else {}),
            **kwargs,
        )

    def log_retry_attempt(
        self,
        operation: str,
        attempt: int,
        max_attempts: int,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Log a retry attempt for a failed operation.

        Args:
            operation: Name of the operation being retried.
            attempt: Current attempt number (1-based).
            max_attempts: Maximum number of attempts.
            **kwargs: Additional context fields.
        """
        self.warning(
            "retry_attempt",
            operation=operation,
            attempt=attempt,
            max_attempts=max_attempts,
            **kwargs,
        )

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def component(self) -> str:
        """Component name bound to this logger instance.

        Returns:
            Component name string.
        """
        return self._component
