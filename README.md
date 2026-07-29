# RKGB — Research Knowledge Graph Builder

> Enterprise-grade AI platform for scientific knowledge extraction, semantic graph construction, and GraphRAG-powered research intelligence.

---

## Project Vision

RKGB is a modular AI infrastructure platform designed to:

- **Ingest and manage** research papers and scientific documents
- **Extract structured knowledge** using NLP and LLM pipelines
- **Construct semantic knowledge graphs** backed by Neo4j
- **Enable GraphRAG** — graph-augmented retrieval-augmented generation
- **Power autonomous research agents** with ontology-driven reasoning
- **Serve as a long-term AI infrastructure platform** for research intelligence

The platform is engineered to the same quality bar as production systems such as LangChain, Apache Airflow, or Microsoft Semantic Kernel — prioritising maintainability, extensibility, modularity, and testability over minimal code.

---

## Architecture Overview

RKGB follows **Clean Architecture**, **Domain-Driven Design (DDD)**, **CQRS-lite**, and an **Event-Driven Pipeline** model.

```
Presentation Layer          FastAPI · CLI · AI Agents · Scheduled Jobs
        ↓
Processing Engine           Pipeline Manager · DSL · Stage Registry · Plugin Loader
        ↓
Application Layer           Commands · Queries · Handlers · DTOs · Policies · Events
        ↓
Domain Layer                Entities · Value Objects · Aggregates · Domain Services
        ↓
Repository Layer            Interfaces (Domain) + Implementations (Infrastructure)
        ↓
Infrastructure Layer        Neo4j · File Storage · Logging · Event Bus · Cache
```

See [`docs/architecture.md`](docs/architecture.md) for detailed layer responsibilities.

---

## Package Structure

| Package | Responsibility |
|---|---|
| `app/` | Entry point, bootstrap, server lifecycle |
| `application/` | CQRS-lite: commands, queries, handlers, DTOs, policies per capability |
| `domain/` | Entities, aggregates, value objects, repository interfaces, domain events |
| `infrastructure/` | Concrete implementations: Neo4j, file storage, cache, messaging, DI |
| `processing/` | Pipeline engine: runtime, DSL, stage registry, plugin loader, contracts |
| `pipelines/` | Twelve domain pipelines — stages (orchestration only), config, events |
| `presentation/` | FastAPI routers, CLI, agents, scheduled jobs |
| `shared/` | Cross-cutting utilities, interfaces, types, constants, base exceptions |
| `tests/` | Unit, integration, and e2e test suites |

---

## Business Capabilities

Each capability owns its own slice of the application layer:

1. Document Management
2. Document Extraction
3. Knowledge Extraction
4. Entity Resolution
5. Ontology Mapping
6. Knowledge Graph Construction
7. Graph Validation
8. Semantic Indexing
9. GraphRAG
10. Research Intelligence
11. Export
12. Maintenance

---

## Setup Instructions

### Prerequisites

- Python 3.12+
- Docker & Docker Compose (for infrastructure services)
- `pip` or `uv`

### Quick Start (host-only, no Docker)

```bash
# 1. Clone the repository
git clone <repo-url> && cd rkgb

# 2. Install all dependencies
make install-dev

# 3. Copy and configure environment
cp .env.example .env
# Edit .env with your Neo4j credentials and other settings

# 4. Start the development server
make run
```

### With Docker

```bash
# Start all infrastructure services + the application
make docker-up

# Tail logs
make docker-logs
```

The API will be available at `http://localhost:8000`.
Neo4j Browser will be available at `http://localhost:7474`.

---

## Development Workflow

```bash
make install-dev    # Install all dev dependencies + pre-commit hooks
make lint           # Run Ruff linter
make format         # Run Black + isort
make type-check     # Run MyPy
make test           # Run all tests
make coverage       # Run tests with coverage report
make check          # Run all quality checks (no fixes)
make clean          # Remove build artefacts and caches
```

---

## Technology Stack

| Concern | Technology |
|---|---|
| API Framework | FastAPI |
| Data Validation | Pydantic v2 |
| Graph Database | Neo4j 5.x |
| Dependency Injection | Lagom |
| Logging | Structlog |
| Linting | Ruff |
| Formatting | Black + isort |
| Type Checking | MyPy (strict) |
| Testing | Pytest + pytest-asyncio |
| Containerisation | Docker Compose |

---

## Documentation

- [`docs/architecture.md`](docs/architecture.md) — Layered architecture reference
- [`docs/project_structure.md`](docs/project_structure.md) — Full directory tree with explanations
- [`docs/api.md`](docs/api.md) — API endpoint reference
- [`docs/developer-guide.md`](docs/developer-guide.md) — Developer onboarding guide
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — Contribution guidelines
- [`CHANGELOG.md`](CHANGELOG.md) — Version history

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines on branching, commits, testing, and pull requests.

---

## License

See [`LICENSE`](LICENSE).
