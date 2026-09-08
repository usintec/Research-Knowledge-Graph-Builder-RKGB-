# Research Knowledge Graph Builder (RKGB)

# Implementation Specification

## Document 01 — Project Structure

**Version:** 1.0

---

# 1. Purpose

This document defines the physical organization of the RKGB codebase.

The objective is to create a scalable, modular, and maintainable project structure that aligns with the Architecture Blueprint, Domain Model Specification, Ontology Specification, and future implementation phases.

The project follows:

* Domain-Driven Design (DDD)
* Clean Architecture
* SOLID Principles
* Modular Monolith Architecture
* Pipeline Architecture
* Event-Driven Architecture

The directory structure should remain stable as the platform evolves.

---

# 2. High-Level Repository Layout

```text
rkgb/
│
├── app/
├── config/
├── data/
├── docker/
├── docs/
├── scripts/
├── tests/
├── tools/
├── .github/
├── pyproject.toml
├── uv.lock
├── Dockerfile
├── docker-compose.yml
├── .env
├── .env.example
├── README.md
├── LICENSE
└── Makefile
```

---

# 3. Application Layer

The `app` directory contains all production code.

```text
app/
│
├── core/
├── shared/
├── domain/
├── application/
├── infrastructure/
├── api/
├── pipeline/
├── events/
├── graph/
├── ontology/
├── parsers/
├── nlp/
├── embeddings/
├── search/
├── agents/
├── ml/
├── monitoring/
└── main.py
```

Each folder represents a subsystem rather than a technical utility.

---

# 4. Core

```text
core/
│
├── bootstrap.py
├── container.py
├── lifecycle.py
├── settings.py
├── constants.py
├── exceptions.py
└── security.py
```

Responsibilities

* Application startup
* Dependency injection
* Configuration loading
* Global constants
* Security
* Shared exceptions

This module should have minimal business logic.

---

# 5. Shared

```text
shared/
│
├── base/
├── enums/
├── value_objects/
├── utils/
├── validators/
├── logging/
├── serialization/
└── types/
```

Contains reusable components shared across all modules.

Examples

* UUID generation
* FileSize
* Checksum
* ProcessingStatus
* Logger
* Time utilities

No domain-specific business rules belong here.

---

# 6. Domain

The domain layer contains the core business model.

```text
domain/
│
├── document/
├── publication/
├── people/
├── organization/
├── dataset/
├── algorithm/
├── experiment/
├── ontology/
├── graph/
└── common/
```

Each package represents one bounded context.

---

Example

```text
domain/document/
│
├── entities/
├── value_objects/
├── repositories/
├── services/
├── events/
└── policies/
```

---

# 7. Application Layer

Coordinates use cases.

```text
application/
│
├── commands/
├── queries/
├── handlers/
├── dto/
├── mappers/
└── services/
```

Responsibilities

* Upload document
* Process document
* Build graph
* Search graph

No persistence logic belongs here.

---

# 8. Infrastructure

Contains implementation details.

```text
infrastructure/
│
├── storage/
├── persistence/
├── database/
├── neo4j/
├── cache/
├── messaging/
├── pdf/
├── embedding/
├── ai/
└── external/
```

Examples

* Neo4j implementation
* SQLite/PostgreSQL
* Local storage
* Amazon S3
* Redis
* Kafka
* spaCy
* Hugging Face

Everything here can be replaced without affecting business logic.

---

# 9. API

```text
api/
│
├── routes/
├── schemas/
├── dependencies/
├── middleware/
├── responses/
└── versioning/
```

Responsibilities

* REST endpoints
* Request validation
* Authentication
* API versioning
* Response serialization

---

# 10. Processing Pipeline

```text
pipeline/
│
├── manager.py
├── context.py
├── interfaces.py
├── executor.py
├── registry.py
├── results.py
├── stages/
└── policies/
```

The pipeline executes processing stages sequentially.

---

Pipeline Stages

```text
stages/
│
├── validation/
├── metadata/
├── duplicate/
├── versioning/
├── storage/
├── indexing/
├── parsing/
├── nlp/
├── graph/
└── export/
```

Each stage performs exactly one responsibility.

---

# 11. Events

```text
events/
│
├── bus/
├── publishers/
├── subscribers/
├── handlers/
├── events/
└── dispatchers/
```

Responsibilities

* Event publishing
* Event subscription
* Dispatching
* Retry
* Logging

Initially uses an in-process event bus.

Future implementations may use Kafka.

---

# 12. Graph

```text
graph/
│
├── builder/
├── repository/
├── cypher/
├── schema/
├── validators/
├── exporters/
└── analytics/
```

Responsibilities

* Graph construction
* Cypher generation
* Validation
* RDF export
* OWL export

---

# 13. Ontology

```text
ontology/
│
├── vocabulary/
├── taxonomy/
├── mappings/
├── rules/
├── inference/
└── validators/
```

Contains the semantic knowledge of the platform.

---

# 14. Parsers

```text
parsers/
│
├── pdf/
├── tables/
├── figures/
├── references/
├── sections/
└── layout/
```

Responsible for document understanding.

---

# 15. NLP

```text
nlp/
│
├── tokenizer/
├── ner/
├── linking/
├── relations/
├── keywords/
├── topics/
├── summarization/
└── embeddings/
```

Contains every NLP component.

---

# 16. Search

```text
search/
│
├── semantic/
├── keyword/
├── vector/
├── graph/
└── ranking/
```

Supports

* Full-text search
* Semantic search
* Graph search
* Hybrid retrieval

---

# 17. Agents (Future)

```text
agents/
│
├── planner/
├── tools/
├── memory/
├── reasoning/
├── workflows/
└── research_assistant/
```

Reserved for Phase 3 (Agentic AI).

---

# 18. Graph Machine Learning (Future)

```text
ml/
│
├── embeddings/
├── node2vec/
├── graphsage/
├── gcn/
├── gat/
├── link_prediction/
└── recommendation/
```

Reserved for Phase 4.

---

# 19. Monitoring

```text
monitoring/
│
├── metrics/
├── tracing/
├── health/
├── profiling/
└── dashboards/
```

Supports observability.

---

# 20. Configuration

```text
config/
│
├── development.yaml
├── testing.yaml
├── production.yaml
└── logging.yaml
```

Configuration is environment-specific.

No hardcoded values should appear in the codebase.

---

# 21. Data Directory

```text
data/
│
├── raw/
├── uploads/
├── processed/
├── cache/
├── exports/
├── embeddings/
├── neo4j/
├── temp/
└── archive/
```

Used only for runtime data.

No source code belongs here.

---

# 22. Documentation

```text
docs/
│
├── architecture/
├── ontology/
├── implementation/
├── adr/
├── api/
├── diagrams/
└── tutorials/
```

Documentation evolves alongside the code.

---

# 23. Tests

```text
tests/
│
├── unit/
├── integration/
├── pipeline/
├── api/
├── graph/
├── ontology/
├── performance/
└── fixtures/
```

Tests mirror the production structure.

Every module should have corresponding tests.

---

# 24. Development Scripts

```text
scripts/
│
├── setup.py
├── seed_database.py
├── import_papers.py
├── export_graph.py
├── clean.py
└── benchmark.py
```

Automation scripts only.

---

# 25. Design Rules

The following rules govern the codebase:

1. Business logic resides only in the Domain and Application layers.
2. Infrastructure must never contain business rules.
3. Domain models must not depend on FastAPI, Neo4j, or storage libraries.
4. Communication between subsystems occurs through interfaces or events.
5. Pipeline stages must be independent and composable.
6. New functionality should be added by extending modules, not modifying unrelated code.
7. Every public module must include unit tests and documentation.

---

# 26. Dependency Direction

```text
API
 │
 ▼
Application
 │
 ▼
Domain
 ▲
 │
Infrastructure
```

The Domain layer has no knowledge of Infrastructure.

Infrastructure depends on Domain—not the other way around.

---

# 27. Future Evolution

The repository structure is intentionally designed to support future capabilities without restructuring the codebase.

Planned additions include:

* RDF and OWL reasoning
* GraphRAG
* Agentic AI
* Kafka event streaming
* Apache Spark processing
* Apache Airflow orchestration
* Feature Store integration
* MLOps pipelines
* Distributed graph analytics

These capabilities should integrate by adding new modules rather than reorganizing existing ones.

---

# 28. Guiding Principle

The project structure is an architectural reflection of the RKGB platform.

Folders represent business capabilities rather than libraries or technologies. This organization promotes modularity, scalability, testability, and long-term maintainability while allowing the platform to evolve from a single-developer research project into a production-grade AI Research Intelligence Platform.
