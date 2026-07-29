# RKGB — Research Knowledge Graph Builder

## Project Overview

Enterprise-grade AI platform for scientific knowledge extraction, semantic graph construction, and GraphRAG-powered research intelligence. Built on Clean Architecture, Domain-Driven Design (DDD), CQRS-lite, and an Event-Driven Pipeline model.

**Current status:** Step A1 complete — full project skeleton bootstrapped. No business logic implemented yet.

## How to Run

```bash
# Install all dependencies (once)
pip install -e ".[dev]"
pip install -e ".[lint]"

# Start the development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API is accessible at port **8000**. Health check: `GET /health`.
Interactive docs: `GET /docs`.

## Stack

| Concern | Technology |
|---|---|
| API | FastAPI + uvicorn |
| Data validation | Pydantic v2 |
| Graph database | Neo4j 5.x (via Docker) |
| DI container | Lagom |
| Logging | Structlog |
| Linting | Ruff + Black + isort |
| Type checking | MyPy (strict) |
| Testing | Pytest + pytest-asyncio |

## Key Directories

| Directory | Purpose |
|---|---|
| `app/` | Entry point — FastAPI app factory |
| `application/` | CQRS-lite slices (commands, queries, handlers, DTOs) |
| `domain/` | Entities, aggregates, value objects, repository interfaces |
| `infrastructure/` | Neo4j, storage, cache, DI container adapters |
| `processing/` | Pipeline engine (runtime, DSL, stage registry) |
| `pipelines/` | Twelve domain pipelines |
| `presentation/` | FastAPI routers, CLI, agents |
| `shared/` | Cross-cutting utilities and base exceptions |
| `tests/` | Unit, integration, e2e suites |
| `configs/` | Environment YAML configs (dev/test/prod) |
| `docs/` | Architecture and project-structure docs |

## Developer Workflow

```bash
make install-dev   # Install all deps + pre-commit hooks
make lint          # Ruff linter
make format        # Black + isort
make type-check    # MyPy
make test          # All tests
make coverage      # Tests + coverage report
make clean         # Remove build artefacts
```

## Architecture Principles

- Pipeline stages contain **orchestration only** — no business logic
- Business logic lives in **command/query handlers**
- Handlers access the domain via **repository interfaces**, never concrete impls
- All cross-cutting concerns (logging, metrics) handled by **infrastructure adapters**
- No circular imports — enforced by Ruff and MyPy
- Async-first for all I/O-bound operations

## User Preferences

- Python 3.11 (Replit environment); 3.12+ syntax is a future upgrade target
- Follow the implementation spec in `attached_assets/` for step-by-step build phases
- Architecture must not be redesigned unless implementation exposes a genuine engineering problem
- Optimise for maintainability, extensibility, modularity, readability, and testability — not minimal code
- Google-style docstrings, type hints everywhere, `pathlib.Path` over `os.path`
