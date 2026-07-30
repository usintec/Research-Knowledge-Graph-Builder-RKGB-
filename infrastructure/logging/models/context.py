"""Correlation context model for the RKGB Logging Framework.

``CorrelationContext`` is an immutable dataclass that flows through every
layer of the system — from an inbound API request down through pipelines,
commands, handlers, and repositories — ensuring a single correlation ID
ties all related log entries together.

Usage::

    from infrastructure.logging.models.context import CorrelationContext
    from infrastructure.logging.correlation import generate_correlation_id

    ctx = CorrelationContext(correlation_id=generate_correlation_id())
    child = ctx.with_pipeline(pipeline_id="pipe-123", execution_id="exec-456")
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any


@dataclass(frozen=True)
class CorrelationContext:
    """Immutable context object that carries tracing identifiers across layers.

    Every field is optional except ``correlation_id``.  Additional fields can
    be set as the context flows deeper into the system (e.g. once a pipeline
    starts, ``pipeline_id`` is added via :meth:`with_pipeline`).

    Attributes:
        correlation_id: Primary tracing identifier — ties all log entries for
            a single logical operation together.
        trace_id: Optional OpenTelemetry-compatible trace identifier.  Set
            once OTEL integration is enabled.
        pipeline_id: Identifier of the active pipeline execution.
        stage_id: Identifier of the active pipeline stage.
        execution_id: Unique identifier for a specific execution run.
        command_name: Name of the command being handled (CQRS command bus).
        query_name: Name of the query being handled (CQRS query bus).
        event_name: Name of the event being processed (event bus).
        user_id: Authenticated user identifier (future — not yet populated).
        plugin_id: Active plugin identifier (future — not yet populated).
        extra: Arbitrary additional key-value pairs for extensibility.
    """

    correlation_id: str
    trace_id: str | None = None
    pipeline_id: str | None = None
    stage_id: str | None = None
    execution_id: str | None = None
    command_name: str | None = None
    query_name: str | None = None
    event_name: str | None = None
    user_id: str | None = None  # future
    plugin_id: str | None = None  # future
    extra: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Derived contexts — return new frozen instances via dataclasses.replace
    # ------------------------------------------------------------------

    def with_pipeline(
        self,
        *,
        pipeline_id: str,
        execution_id: str | None = None,
    ) -> "CorrelationContext":
        """Return a new context enriched with pipeline identifiers.

        Args:
            pipeline_id: The pipeline identifier.
            execution_id: Optional execution run identifier.

        Returns:
            New :class:`CorrelationContext` with pipeline fields set.
        """
        return replace(self, pipeline_id=pipeline_id, execution_id=execution_id)

    def with_stage(self, *, stage_id: str) -> "CorrelationContext":
        """Return a new context enriched with a stage identifier.

        Args:
            stage_id: The stage identifier.

        Returns:
            New :class:`CorrelationContext` with ``stage_id`` set.
        """
        return replace(self, stage_id=stage_id)

    def with_command(self, *, command_name: str) -> "CorrelationContext":
        """Return a new context enriched with a command name.

        Args:
            command_name: Fully-qualified command class name.

        Returns:
            New :class:`CorrelationContext` with ``command_name`` set.
        """
        return replace(self, command_name=command_name)

    def with_query(self, *, query_name: str) -> "CorrelationContext":
        """Return a new context enriched with a query name.

        Args:
            query_name: Fully-qualified query class name.

        Returns:
            New :class:`CorrelationContext` with ``query_name`` set.
        """
        return replace(self, query_name=query_name)

    def with_event(self, *, event_name: str) -> "CorrelationContext":
        """Return a new context enriched with an event name.

        Args:
            event_name: Fully-qualified event class name.

        Returns:
            New :class:`CorrelationContext` with ``event_name`` set.
        """
        return replace(self, event_name=event_name)

    def with_trace(self, *, trace_id: str) -> "CorrelationContext":
        """Return a new context enriched with an OpenTelemetry trace ID.

        Args:
            trace_id: OTEL-compatible trace identifier.

        Returns:
            New :class:`CorrelationContext` with ``trace_id`` set.
        """
        return replace(self, trace_id=trace_id)

    def with_extra(self, **kwargs: Any) -> "CorrelationContext":  # noqa: ANN401
        """Return a new context with additional arbitrary key-value pairs.

        Args:
            **kwargs: Arbitrary key-value context fields.

        Returns:
            New :class:`CorrelationContext` with ``extra`` updated.
        """
        merged = {**self.extra, **kwargs}
        return replace(self, extra=merged)

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_log_dict(self) -> dict[str, Any]:
        """Return a flat dictionary of all non-None context fields.

        Only populated fields are included so log entries stay concise.

        Returns:
            Dict suitable for merging into a structlog event dictionary.
        """
        data: dict[str, Any] = {"correlation_id": self.correlation_id}
        optional_fields: dict[str, Any] = {
            "trace_id": self.trace_id,
            "pipeline_id": self.pipeline_id,
            "stage_id": self.stage_id,
            "execution_id": self.execution_id,
            "command_name": self.command_name,
            "query_name": self.query_name,
            "event_name": self.event_name,
            "user_id": self.user_id,
            "plugin_id": self.plugin_id,
        }
        for key, value in optional_fields.items():
            if value is not None:
                data[key] = value
        if self.extra:
            data.update(self.extra)
        return data
