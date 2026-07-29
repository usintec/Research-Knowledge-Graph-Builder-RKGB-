# RKGB — Project Structure

This document describes the physical layout of the repository and the purpose of every top-level directory and key sub-package.

---

## Top-Level Layout

```
rkgb/                           ← Repository root
│
├── app/                        ← Application entry point
├── application/                ← CQRS-lite slices (one per capability)
├── domain/                     ← Domain model (entities, aggregates, …)
├── infrastructure/             ← External service adapters
├── processing/                 ← Pipeline orchestration engine
├── pipelines/                  ← Twelve domain pipelines
├── presentation/               ← Inbound adapters (FastAPI, CLI, agents)
├── shared/                     ← Cross-cutting utilities and base types
│
├── tests/                      ← Test suites
├── docs/                       ← Documentation
├── configs/                    ← Environment configuration files
├── scripts/                    ← Operational and utility scripts
├── docker/                     ← Dockerfiles
├── examples/                   ← Usage examples
├── tools/                      ← Developer tooling scripts
├── resources/                  ← Static resources (ontologies, schemas)
│
├── pyproject.toml              ← Project metadata, dependencies, tool config
├── Makefile                    ← Developer workflow shortcuts
├── docker-compose.yml          ← Local development infrastructure
├── .env.example                ← Environment variable template
├── .pre-commit-config.yaml     ← Pre-commit hook configuration
├── .gitignore
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE
```

---

## `app/` — Entry Point

```
app/
└── main.py                     ← FastAPI app factory + server entry point
```

---

## `application/` — CQRS-lite Capabilities

```
application/
├── common/                     ← Shared base classes (BaseCommand, BaseQuery, …)
├── document_management/
├── document_extraction/
├── knowledge_extraction/
├── entity_resolution/
├── ontology_mapping/
├── graph_construction/
├── graph_validation/
├── semantic_indexing/
├── graph_rag/
├── research_intelligence/
├── export/
└── maintenance/
```

Each capability slice follows this internal layout:

```
<capability>/
├── commands/           ← Command dataclasses
├── command_handlers/   ← Command handlers
├── queries/            ← Query dataclasses
├── query_handlers/     ← Query handlers
├── dto/                ← Data Transfer Objects
├── results/            ← Result types
├── events/             ← Application events
├── validators/         ← Input validators
├── policies/           ← Business rule policies
└── tests/              ← Capability-scoped tests
```

---

## `domain/` — Domain Model

```
domain/
├── entities/           ← Domain entities (identity + lifecycle)
├── aggregates/         ← Aggregate roots (consistency boundaries)
├── value_objects/      ← Immutable, equality-by-value types
├── repositories/       ← Repository interfaces (abstract contracts)
├── services/           ← Stateless domain services
├── events/             ← Domain events
├── exceptions/         ← Domain exception hierarchy
└── specifications/     ← Composable rule specifications
```

---

## `infrastructure/` — External Adapters

```
infrastructure/
├── config/             ← Settings loading (Pydantic Settings)
├── logging/            ← Structlog configuration
├── database/           ← Database connection management
├── neo4j/              ← Neo4j driver adapter
├── storage/            ← File / object storage adapter
├── messaging/          ← Event bus adapter (in-process / Kafka)
├── security/           ← Auth, secrets management
├── cache/              ← Redis cache adapter
├── monitoring/         ← Health checks, metrics
├── repositories/       ← Concrete repository implementations
├── pdf/                ← PDF parsing adapters
├── embeddings/         ← LLM embedding adapters
├── vector_store/       ← Vector database adapters
└── dependency_injection/ ← DI container bootstrap
```

---

## `processing/` — Pipeline Engine

```
processing/
├── pipeline/           ← Pipeline orchestrator
├── runtime/            ← Async execution runtime
├── registry/           ← Stage registry
├── plugins/            ← Plugin discovery and loading
├── dsl/                ← Pipeline definition DSL
├── context/            ← Pipeline execution context
├── contracts/          ← Stage base classes and interfaces
├── execution/          ← Execution strategies (sequential, parallel)
├── events/             ← Engine lifecycle events
└── exceptions/         ← Engine exception hierarchy
```

---

## `pipelines/` — Twelve Domain Pipelines

```
pipelines/
├── document_management/
├── document_extraction/
├── knowledge_extraction/
├── entity_resolution/
├── ontology_mapping/
├── knowledge_graph_construction/
├── graph_validation/
├── semantic_indexing/
├── graph_rag/
├── research_intelligence/
├── export/
└── maintenance/
```

Each pipeline follows this layout:

```
<pipeline>/
├── pipeline/       ← Pipeline class definition
├── stages/         ← Individual pipeline stage implementations
├── events/         ← Pipeline-specific events
├── config/         ← Pipeline configuration schema
└── tests/          ← Pipeline tests
```

---

## `presentation/` — Inbound Adapters

```
presentation/
├── api/            ← FastAPI routers and request/response models
├── cli/            ← CLI commands (Typer / Click)
├── agents/         ← Autonomous AI agent definitions
└── jobs/           ← Scheduled background jobs
```

---

## `shared/` — Cross-Cutting

```
shared/
├── constants/      ← Application-wide constants
├── utils/          ← Pure utility functions
├── types/          ← Custom type aliases and TypeVars
├── interfaces/     ← Generic abstract interfaces
├── exceptions/     ← Base exception hierarchy
└── models/         ← Base Pydantic / dataclass models
```

---

## `tests/` — Test Suites

```
tests/
├── unit/           ← Pure unit tests (no I/O, no external services)
├── integration/    ← Tests requiring external services (Neo4j, Redis)
├── e2e/            ← End-to-end API and pipeline tests
├── fixtures/       ← Shared pytest fixtures and factories
└── conftest.py     ← Root pytest configuration
```
