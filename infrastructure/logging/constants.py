"""Constants for the RKGB Logging & Observability Framework.

Centralising magic strings here prevents them from scattering across the
codebase and makes future refactoring safe.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Logger names
# ---------------------------------------------------------------------------

#: Root logger name for the RKGB platform.
ROOT_LOGGER_NAME: str = "rkgb"

#: Logger name for the pipeline engine.
PIPELINE_LOGGER_NAME: str = "rkgb.pipeline"

#: Logger name for the command bus.
COMMAND_BUS_LOGGER_NAME: str = "rkgb.command_bus"

#: Logger name for the query bus.
QUERY_BUS_LOGGER_NAME: str = "rkgb.query_bus"

#: Logger name for the event bus.
EVENT_BUS_LOGGER_NAME: str = "rkgb.event_bus"

#: Logger name for infrastructure components.
INFRASTRUCTURE_LOGGER_NAME: str = "rkgb.infrastructure"

# ---------------------------------------------------------------------------
# Context variable keys
# ---------------------------------------------------------------------------

#: Key used for the correlation ID in structured log entries.
KEY_CORRELATION_ID: str = "correlation_id"

#: Key used for the trace ID in structured log entries.
KEY_TRACE_ID: str = "trace_id"

#: Key used for the pipeline ID in structured log entries.
KEY_PIPELINE_ID: str = "pipeline_id"

#: Key used for the stage ID in structured log entries.
KEY_STAGE_ID: str = "stage_id"

#: Key used for the execution ID in structured log entries.
KEY_EXECUTION_ID: str = "execution_id"

#: Key used for command name in structured log entries.
KEY_COMMAND_NAME: str = "command_name"

#: Key used for query name in structured log entries.
KEY_QUERY_NAME: str = "query_name"

#: Key used for event name in structured log entries.
KEY_EVENT_NAME: str = "event_name"

#: Key used for the component/module name.
KEY_COMPONENT: str = "component"

#: Key used for exception details.
KEY_EXCEPTION: str = "exception"

#: Key used for duration measurements (seconds).
KEY_DURATION_MS: str = "duration_ms"

#: Key used for user identifier (future).
KEY_USER_ID: str = "user_id"

#: Key used for plugin identifier (future).
KEY_PLUGIN_ID: str = "plugin_id"

# ---------------------------------------------------------------------------
# Third-party loggers to suppress in production
# ---------------------------------------------------------------------------

#: Standard third-party loggers that are suppressed when
#: ``LoggingConfig.suppress_third_party`` is ``True``.
THIRD_PARTY_LOGGERS: tuple[str, ...] = (
    "uvicorn",
    "uvicorn.access",
    "uvicorn.error",
    "fastapi",
    "asyncio",
    "neo4j",
    "httpx",
    "httpcore",
    "hpack",
    "h2",
)

# ---------------------------------------------------------------------------
# Handler identifiers
# ---------------------------------------------------------------------------

#: Identifier for the console (stdout) handler.
HANDLER_CONSOLE: str = "console"

#: Identifier for the plain-text file handler.
HANDLER_FILE: str = "file"

#: Identifier for the JSON file handler.
HANDLER_JSON_FILE: str = "json_file"

#: Identifier for the rotating file handler.
HANDLER_ROTATING_FILE: str = "rotating_file"

# ---------------------------------------------------------------------------
# Format identifiers
# ---------------------------------------------------------------------------

#: Human-readable console format (for development).
FORMAT_CONSOLE: str = "console"

#: Machine-parseable JSON format (for production / log aggregation).
FORMAT_JSON: str = "json"

# ---------------------------------------------------------------------------
# Lifecycle event messages
# ---------------------------------------------------------------------------

#: Emitted when the logging framework is fully initialised.
MSG_LOGGING_INITIALISED: str = "Logging framework initialised."

#: Emitted when the logging framework is shut down.
MSG_LOGGING_SHUTDOWN: str = "Logging framework shut down."
