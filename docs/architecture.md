# RKGB — Architecture Reference

## Layered Architecture

RKGB follows Clean Architecture with five discrete layers. Dependencies flow strictly **inward** — outer layers may depend on inner layers, never the reverse.

```
┌─────────────────────────────────────────────────────┐
│               Presentation Layer                    │
│  FastAPI · CLI · AI Agents · Jobs · Kafka Consumers │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│               Processing Engine                     │
│  Pipeline Manager · DSL · Stage Registry · Plugins  │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              Application Layer (CQRS-lite)          │
│  Commands · Queries · Handlers · DTOs · Policies    │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                   Domain Layer                      │
│  Entities · Aggregates · Value Objects · Services   │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│               Infrastructure Layer                  │
│  Neo4j · Storage · Cache · Messaging · Logging      │
└─────────────────────────────────────────────────────┘
```

---

## Layer Responsibilities

### Presentation Layer (`presentation/`)
Entry points into the system. All presentation adapters translate external input into Application Layer commands or queries.

- **FastAPI** — REST API routers and request/response models.
- **CLI** — Command-line interface for administrative tasks.
- **Agents** — Autonomous AI agents that drive pipeline execution.
- **Jobs** — Scheduled background tasks.
- **Kafka Consumers** — Event-driven pipeline triggers (future).

### Processing Engine (`processing/`)
The pipeline orchestration engine. Manages execution of domain pipelines without containing any business logic.

- **Pipeline Manager** — Coordinates pipeline execution lifecycle.
- **Runtime** — Async pipeline execution runtime.
- **DSL** — Declarative pipeline definition language.
- **Stage Registry** — Resolves and instantiates pipeline stages.
- **Plugin Loader** — Discovers and loads pipeline stage plugins.
- **Context** — Carries state through a pipeline execution.
- **Contracts** — Abstract base for all pipeline stages.
- **Events** — Pipeline lifecycle events.
- **Exceptions** — Pipeline-specific error hierarchy.

### Application Layer (`application/`)
CQRS-lite slices, one per business capability. All business behaviour is implemented here.

Each capability contains:
- `commands/` — Command dataclasses (intent to mutate state).
- `command_handlers/` — Handlers that execute commands via the domain.
- `queries/` — Query dataclasses (intent to read state).
- `query_handlers/` — Handlers that fulfil queries via repositories.
- `dto/` — Data Transfer Objects for input/output.
- `results/` — Result types returned by handlers.
- `events/` — Application events published after handler execution.
- `validators/` — Input validation logic.
- `policies/` — Business rule enforcement.

### Domain Layer (`domain/`)
The core of the system. Has zero dependencies on outer layers.

- `entities/` — Objects with identity and lifecycle.
- `aggregates/` — Consistency boundaries (roots of entity clusters).
- `value_objects/` — Immutable, equality-by-value objects.
- `repositories/` — Abstract repository interfaces (contracts only).
- `services/` — Stateless domain operations that span aggregates.
- `events/` — Domain events raised by aggregates.
- `exceptions/` — Domain-specific error types.
- `specifications/` — Composable business rule objects.

### Infrastructure Layer (`infrastructure/`)
Concrete implementations of all interfaces defined in the domain and application layers.

- `neo4j/` — Neo4j graph database adapter.
- `storage/` — File and object storage adapters.
- `messaging/` — Event bus adapters (in-process; Kafka future).
- `cache/` — Redis cache adapter.
- `embeddings/` — LLM embedding adapters.
- `vector_store/` — Vector database adapters.
- `repositories/` — Concrete repository implementations.
- `dependency_injection/` — DI container bootstrap.
- `config/` — Settings loading and validation.
- `logging/` — Structlog configuration.
- `monitoring/` — Metrics and health check endpoints.

---

## CQRS-Lite Data Flow

Pipeline stages never access repositories directly. All state mutation and queries flow through the command/query bus:

```
Pipeline Stage
    ↓ dispatch(command) / dispatch(query)
Command Bus / Query Bus
    ↓
Handler
    ↓
Domain (Aggregates / Services)
    ↓
Repository Interface
    ↓
Infrastructure (Neo4j, Storage, …)
```

---

## Business Capabilities → Pipelines

| Capability | Pipeline |
|---|---|
| Document Management | Document Management Pipeline |
| Document Extraction | Document Extraction Pipeline |
| Knowledge Extraction | Knowledge Extraction Pipeline |
| Entity Resolution | Entity Resolution Pipeline |
| Ontology Mapping | Ontology Mapping Pipeline |
| Graph Construction | Knowledge Graph Construction Pipeline |
| Graph Validation | Graph Validation Pipeline |
| Semantic Indexing | Semantic Indexing Pipeline |
| GraphRAG | GraphRAG Pipeline |
| Research Intelligence | Research Intelligence Pipeline |
| Export | Export Pipeline |
| Maintenance | Maintenance Pipeline |

---

## Architectural Decision Records

| ADR | Decision |
|---|---|
| ADR-001 | Clean Architecture layering |
| ADR-002 | Pipeline pattern for processing |
| ADR-003 | In-process event bus (Kafka roadmap) |
| ADR-004 | Neo4j as primary graph database |
| ADR-005 | FastAPI as HTTP framework |
| ADR-006 | Kafka migration plan |
