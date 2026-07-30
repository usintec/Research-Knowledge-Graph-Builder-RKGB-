"""Structured log entry model for the RKGB Logging Framework.

``LogEntry`` represents a single, fully-formed log event.  It is used
internally by formatters and may be emitted to metrics hooks in the future.
"""

from __future__ import annotations

import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ExceptionInfo:
    """Captured exception details for structured logging.

    Attributes:
        exc_type: Exception class name.
        message: Exception message string.
        traceback: Full stack trace as a single string.
    """

    exc_type: str
    message: str
    traceback: str

    @classmethod
    def from_exception(cls, exc: BaseException) -> "ExceptionInfo":
        """Build an ``ExceptionInfo`` from a live exception.

        Args:
            exc: The caught exception.

        Returns:
            :class:`ExceptionInfo` with all fields populated.
        """
        tb = "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        )
        return cls(
            exc_type=type(exc).__name__,
            message=str(exc),
            traceback=tb.rstrip(),
        )

    def to_dict(self) -> dict[str, str]:
        """Return a plain dict suitable for JSON serialisation.

        Returns:
            Dict with ``exc_type``, ``message``, and ``traceback`` keys.
        """
        return {
            "exc_type": self.exc_type,
            "message": self.message,
            "traceback": self.traceback,
        }


@dataclass
class LogEntry:
    """A fully-formed, structured log event.

    ``LogEntry`` captures everything needed to reconstruct the full context
    of a log event.  It is produced by the ``LoggerFactory`` and can be
    forwarded to metrics backends without re-parsing the log string.

    Future support for OpenTelemetry span export can be added by converting
    the fields here into OTEL ``LogRecord`` attributes.

    Attributes:
        timestamp: UTC time of the log event.
        level: Log level string (e.g. ``"INFO"``).
        logger_name: Name of the logger that produced this entry.
        event: Human-readable log message / event slug.
        correlation_id: Primary trace identifier (may be ``None`` before context
            is set, though this is unusual in well-configured code).
        trace_id: OpenTelemetry trace identifier.
        pipeline_id: Active pipeline identifier.
        stage_id: Active stage identifier.
        execution_id: Execution run identifier.
        command_name: Active command name.
        query_name: Active query name.
        event_name: Active domain event name.
        component: Component / module name.
        duration_ms: Duration in milliseconds (for timed operations).
        exception: Captured exception info, if any.
        extra: Arbitrary additional fields.
    """

    timestamp: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    level: str = "INFO"
    logger_name: str = "rkgb"
    event: str = ""
    correlation_id: str | None = None
    trace_id: str | None = None
    pipeline_id: str | None = None
    stage_id: str | None = None
    execution_id: str | None = None
    command_name: str | None = None
    query_name: str | None = None
    event_name: str | None = None
    component: str | None = None
    duration_ms: float | None = None
    exception: ExceptionInfo | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialise the entry to a flat dictionary.

        Only non-``None`` optional fields are included to keep the output
        concise.

        Returns:
            Dict suitable for JSON serialisation or structlog event dicts.
        """
        data: dict[str, Any] = {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "logger": self.logger_name,
            "event": self.event,
        }
        optional: dict[str, Any] = {
            "correlation_id": self.correlation_id,
            "trace_id": self.trace_id,
            "pipeline_id": self.pipeline_id,
            "stage_id": self.stage_id,
            "execution_id": self.execution_id,
            "command_name": self.command_name,
            "query_name": self.query_name,
            "event_name": self.event_name,
            "component": self.component,
            "duration_ms": self.duration_ms,
        }
        for key, value in optional.items():
            if value is not None:
                data[key] = value
        if self.exception:
            data["exception"] = self.exception.to_dict()
        if self.extra:
            data.update(self.extra)
        return data
