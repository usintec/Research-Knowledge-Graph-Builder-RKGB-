# Changelog

All notable changes to RKGB will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Step A1: Complete project skeleton and bootstrap.
  - Full layered package structure (`application`, `domain`, `infrastructure`, `processing`, `pipelines`, `presentation`, `shared`).
  - Twelve application capability slices with empty CQRS sub-packages.
  - Twelve domain pipeline packages with stage/event/config/test sub-packages.
  - Processing engine package scaffold (pipeline, runtime, DSL, registry, plugins, contracts, context, execution).
  - Infrastructure package scaffold (Neo4j, storage, messaging, cache, monitoring, embeddings, vector store, DI).
  - `pyproject.toml` with Ruff, Black, isort, MyPy, pytest, and coverage configuration.
  - `Makefile` with install, lint, format, type-check, test, coverage, run, docker, and clean targets.
  - `Dockerfile` and `docker-compose.yml` for local development (app, Neo4j, Redis).
  - `.pre-commit-config.yaml` with Ruff, Black, isort, and MyPy hooks.
  - `.env.example` with all required environment variable placeholders.
  - `configs/` with development, testing, and production YAML stubs.
  - Documentation: `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `docs/architecture.md`, `docs/project_structure.md`.
  - `LICENSE` (MIT).

---

## [0.1.0] — 2026-07-29

- Initial repository import and architecture documentation.

---

[Unreleased]: https://github.com/your-org/rkgb/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/your-org/rkgb/releases/tag/v0.1.0
