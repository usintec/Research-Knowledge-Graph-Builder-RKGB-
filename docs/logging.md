# RKGB Logging & Observability Framework

> Step A3 — Infrastructure Layer

---

## Overview

The RKGB Logging Framework is the observability foundation for the entire platform.  It provides:

- **Structured logging** — every log entry is a machine-parseable key-value record
- **Correlation context propagation** — a single ID ties all log entries for one logical operation together, flowing from HTTP handler through pipelines, commands, repositories, and back
- **Dependency-injection-friendly design** — business code never configures logging directly; it receives a `LoggerFactory` from the DI container
- **Formatter-driven output** — human-readable console output for development, JSON for production log aggregation
- **Future-proof architecture** — designed for seamless OpenTelemetry, Prometheus, Loki, and Kafka integration without API changes

---

## Architecture

The framework lives entirely within the **Infrastructure Layer** and is depended upon by every other layer.

```
┌─────────────────────────────────────────────────────────┐
│                   Presentation Layer                     │
│         (FastAPI middleware — Step A5, future)          │
└────────────────────────┬────────────────────────────────┘
                         │ uses ILogger (protocol)
┌────────────────────────▼────────────────────────────────┐
│                 Application Layer                        │
│    Commands / Queries / Handlers / Event Handlers       │
│    ← receives ILogger via DI, never configures logging  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   Domain Layer                           │
│    Entities / Aggregates / Domain Services              │
│    ← pure domain; no logging dependency                 │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│               Infrastructure Layer ◄──── HERE           │
│                                                         │
│  infrastructure/logging/                                │
│  ├── bootstrap.py       ← single entry point           │
│  ├── manager.py         ← configures structlog + stdlib │
│  ├── factory.py         ← creates component loggers    │
│  ├── logger.py          ← RKGBLogger (ILogger impl)    │
│  ├── context.py         ← contextvars propagation      │
│  ├── correlation.py     ← UUID correlation/trace IDs   │
│  ├── formatter.py       ← console + JSON formatters    │
│  ├── handlers.py        ← console, file, rotating      │
│  ├── filters.py         ← level, sensitive-data, etc.  │
│  ├── middleware.py      ← pipeline/command/query/event │
│  ├── interfaces.py      ← ILogger, ILogHandler, ...    │
│  ├── constants.py       ← magic-free string constants  │
│  ├── exceptions.py      ← typed exception hierarchy    │
│  └── models/                                           │
│      ├── context.py     ← CorrelationContext dataclass │
│      └── log_entry.py   ← LogEntry + ExceptionInfo     │
└─────────────────────────────────────────────────────────┘
```

---

## Logger Lifecycle

```
bootstrap_logging(config_manager)
        │
        ▼
LoggingManager.__init__(LoggingConfig)
        │
        ▼
LoggingManager.initialise()
  ├── Build shared structlog processor chain
  ├── Configure structlog globally (structlog.configure)
  ├── Build handlers (ConsoleLogHandler + optional RotatingFileLogHandler)
  ├── Attach handlers to stdlib root logger
  ├── Suppress noisy third-party loggers (optional)
  └── Create LoggerFactory
        │
        ▼
LoggerFactory.get_logger("my.component")
        │
        ▼
RKGBLogger (wraps structlog BoundLogger)
        │
        ▼
logger.info("event_slug", field1="value1", field2="value2")
```

---

## Correlation Flow

Every entry point sets a `CorrelationContext` via `set_correlation_context()`.  The context automatically flows into every log entry for the current async task through Python's `contextvars` — no explicit parameter passing needed.

```
HTTP Request arrives
        │
        ▼
FastAPI Middleware (future Step A5)
  └── set_correlation_context(CorrelationContext(
          correlation_id=generate_correlation_id()
      ))
        │
        ▼
Command Bus (future)
  └── command_logging(logger, ctx, command_name="CreateDocumentCommand")
      └── ctx.with_command("CreateDocumentCommand")
        │
        ▼
Command Handler
  └── logger.info("processing") → includes correlation_id automatically
        │
        ▼
Repository
  └── logger.debug("query_executed") → same correlation_id
        │
        ▼
Reset context in middleware teardown
  └── reset_correlation_context(token)
```

Every log entry produced during this flow carries the same `correlation_id`, enabling end-to-end traceability in any log aggregation system.

---

## Structured Log Format

### Development (console format)

Human-readable, colourised output using structlog's `ConsoleRenderer`:

```
2026-07-30T09:00:00Z [info     ] pipeline_stage_started  component=pipeline stage_id=extraction correlation_id=3a8f1b2c-...
```

### Production (JSON format)

Single-line JSON objects for log aggregation (Loki, Datadog, CloudWatch, Elastic):

```json
{
  "timestamp": "2026-07-30T09:00:00.000Z",
  "level": "info",
  "logger": "rkgb.pipeline",
  "event": "pipeline_stage_started",
  "component": "pipeline",
  "stage_id": "extraction",
  "correlation_id": "3a8f1b2c-4d5e-6789-abcd-ef0123456789",
  "pipeline_id": "pipe-001",
  "execution_id": "exec-xyz"
}
```

### Standard Fields

| Field | Type | Description |
|---|---|---|
| `timestamp` | ISO 8601 UTC | Time of the event |
| `level` | string | `debug` / `info` / `warning` / `error` / `critical` |
| `logger` | string | Logger name (component path) |
| `event` | string | Event slug (snake_case, machine-readable) |
| `component` | string | Logical component name |
| `correlation_id` | UUID | Primary trace identifier |
| `trace_id` | 32-char hex | OpenTelemetry trace ID (when set) |
| `pipeline_id` | string | Active pipeline identifier |
| `stage_id` | string | Active stage identifier |
| `execution_id` | string | Execution run identifier |
| `command_name` | string | Active command class name |
| `query_name` | string | Active query class name |
| `event_name` | string | Active domain event class name |
| `duration_ms` | float | Operation duration in milliseconds |
| `exception` | object | `{exc_type, message, traceback}` |

---

## Integration Examples

### 1. Application startup (`app/main.py`)

```python
from infrastructure.config.bootstrap import bootstrap_config
from infrastructure.logging.bootstrap import bootstrap_logging

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    config_manager = bootstrap_config()
    logging_manager = bootstrap_logging(config_manager)
    try:
        yield
    finally:
        logging_manager.shutdown()
```

### 2. Service / handler (via DI)

```python
from infrastructure.logging.interfaces import ILogger

class DocumentService:
    def __init__(self, logger: ILogger) -> None:
        self._log = logger

    async def create(self, doc_id: str) -> None:
        self._log.info("creating_document", doc_id=doc_id)
        try:
            # ... create logic ...
            self._log.info("document_created", doc_id=doc_id)
        except Exception as exc:
            self._log.error("document_creation_failed", doc_id=doc_id, exc_info=True)
            raise
```

### 3. Correlation context at an entry point

```python
from infrastructure.logging import (
    CorrelationContext,
    generate_correlation_id,
    set_correlation_context,
    clear_correlation_context,
)

cid = generate_correlation_id()
ctx = CorrelationContext(correlation_id=cid)
token = set_correlation_context(ctx)
try:
    await run_pipeline(ctx)
finally:
    reset_correlation_context(token)
```

### 4. Pipeline stage middleware

```python
from infrastructure.logging.middleware import async_pipeline_stage_logging

async with async_pipeline_stage_logging(
    logger,
    ctx,
    stage_id="extraction_stage",
    pipeline_id="pipe-001",
):
    await stage.execute(context)
# Logs: pipeline_stage_started, pipeline_stage_completed (or pipeline_stage_failed)
```

### 5. Command bus integration (future)

```python
from infrastructure.logging.middleware import command_logging

async with command_logging(logger, ctx, command_name="CreateDocumentCommand"):
    result = await handler.handle(command)
# Logs: command_dispatched, command_completed (or command_failed)
```

### 6. Unit tests

```python
from infrastructure.logging.bootstrap import build_test_logging_manager

def test_my_service():
    manager = build_test_logging_manager()
    logger = manager.factory.get_logger("test_component")
    # ... use logger in tests
    manager.shutdown()
```

---

## Configuration Integration

The framework reads all settings from `LoggingConfig` (Step A2), retrieved via `ConfigManager.get(LoggingConfig)`.  No logging code ever reads environment variables directly.

| Config field | Effect |
|---|---|
| `level` | Minimum log level for all handlers |
| `format` | `"console"` → ColourConsoleRenderer; `"json"` → JSONRenderer |
| `include_timestamp` | Prepend ISO 8601 timestamp |
| `include_caller` | Append `filename:lineno` |
| `file.enabled` | Activate rotating file handler |
| `file.path` | Log file path |
| `file.max_bytes` | Rotation threshold |
| `file.backup_count` | Number of rotated files to keep |
| `suppress_third_party` | Raise uvicorn/neo4j/httpx loggers to WARNING |
| `enable_otel` | Reserved for OpenTelemetry integration |

Environment-specific YAML examples:

```yaml
# configs/development.yaml
logging:
  level: DEBUG
  format: console
  include_caller: true
```

```yaml
# configs/production.yaml
logging:
  level: INFO
  format: json
  file:
    enabled: true
    path: logs/rkgb.log
    max_bytes: 52428800   # 50 MB
    backup_count: 10
  suppress_third_party: true
```

---

## DI Container Integration (Step A4 Preview)

Once the DI container (Lagom) is wired up in Step A4, the logging framework plugs in as follows:

```python
# infrastructure/dependency_injection/container.py

from lagom import Container
from infrastructure.logging.manager import LoggingManager
from infrastructure.logging.factory import LoggerFactory

def build_container(
    config_manager: ConfigManager,
    logging_manager: LoggingManager,
) -> Container:
    container = Container()

    # Singletons
    container.define(ConfigManager, lambda: config_manager)
    container.define(LoggingManager, lambda: logging_manager)
    container.define(LoggerFactory, lambda: logging_manager.factory)

    # Per-component loggers (resolved by component name convention)
    container.define(
        DocumentService,
        lambda: DocumentService(
            logger=logging_manager.factory.get_logger("application.document_service"),
        ),
    )
    return container
```

Business code receives `ILogger` (the protocol) via constructor injection — it never imports `LoggingManager`, `LoggerFactory`, or structlog.

---

## Pipeline Context Integration (Future)

The pipeline engine (Step B) will use :func:`~infrastructure.logging.middleware.async_pipeline_stage_logging` to automatically instrument every stage without modifying stage implementations.

The `CorrelationContext` is enriched at each level:

```
CorrelationContext(correlation_id=...)               ← set at HTTP boundary
  └── .with_pipeline(pipeline_id=..., execution_id=...)   ← set by PipelineManager
       └── .with_stage(stage_id=...)                      ← set per stage
```

Because `CorrelationContext` is an immutable frozen dataclass, each level creates a new instance without mutating the parent — thread-safe and testable.

---

## Best Practices

1. **Never call `structlog.get_logger()` or `logging.getLogger()` in business code** — always use `LoggerFactory.get_logger()`.
2. **Use event slugs, not sentences** — `logger.info("document_created", doc_id=...)` not `logger.info(f"Document {id} was created")`.
3. **Pass structured fields as kwargs** — `logger.error("validation_failed", field="email", reason="invalid format")`.
4. **Use `logger.exception()` from inside `except` blocks** — it automatically captures the traceback.
5. **Bind context at the service level** — `self._log = factory.get_logger("my_service").bind(tenant_id=tenant_id)`.
6. **Never log secrets** — the `SensitiveDataFilter` redacts common fields, but avoid passing secrets as kwargs at all.
7. **Set correlation context at every entry point** — HTTP handler, CLI command, background worker, pipeline run.

---

## Future OpenTelemetry Strategy

The framework is explicitly designed for OTEL integration:

| Current | Future (OTEL enabled) |
|---|---|
| `UUIDCorrelationProvider` generates trace IDs | Replace with `OTELCorrelationProvider` reading from active span |
| `enable_otel: false` in `LoggingConfig` | Set `enable_otel: true` + `otel_exporter_endpoint` |
| Correlation IDs in log fields | OTEL `trace_id` / `span_id` injected by `structlog-opentelemetry` processor |
| No metrics emission | `IMetricsEmitter` protocol wired to Prometheus client |
| Handlers: console + file | Add `OTELLogExporter` handler (OTLP/gRPC) |

When OTEL is activated, no changes to business code or log call sites are needed — only the processor chain and handler list inside `LoggingManager` are updated.

---

## Security

- **`SensitiveDataFilter`** — always-active structlog processor that redacts `password`, `token`, `api_key`, `secret`, `authorization`, and other credential fields to `[REDACTED]`.
- Log files should be stored on volumes with restricted read permissions (`chmod 640`).
- In Kubernetes, mount the log path as an emptyDir volume and ship to Loki/Elastic via a sidecar — never use PersistentVolumes for application logs.
