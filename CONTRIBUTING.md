# Contributing to RKGB

Thank you for taking the time to contribute to the Research Knowledge Graph Builder.

---

## Code of Conduct

Be respectful, constructive, and professional. We welcome contributors of all experience levels.

---

## Development Setup

```bash
git clone <repo-url>
cd rkgb
make install-dev
cp .env.example .env
```

---

## Branching Strategy

| Branch | Purpose |
|---|---|
| `main` | Stable, production-ready code |
| `develop` | Integration branch for feature work |
| `feature/<name>` | New features |
| `fix/<name>` | Bug fixes |
| `chore/<name>` | Tooling, docs, refactors |

**Never commit directly to `main`.**

---

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short summary>

[optional body]

[optional footer(s)]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`

Examples:

```
feat(document_management): add UploadDocumentCommand handler
fix(pipeline): prevent duplicate stage registration
docs(architecture): clarify CQRS-lite data flow
```

---

## Pull Requests

1. Branch off `develop`.
2. Keep PRs focused — one concern per PR.
3. All tests must pass: `make test`.
4. All quality checks must pass: `make check`.
5. Write or update tests for every changed behaviour.
6. Update `CHANGELOG.md` under the `[Unreleased]` section.
7. Request review from at least one team member.

---

## Coding Standards

- **Type hints everywhere** — no `Any` without justification.
- **Google-style docstrings** for all public classes and functions.
- **Dataclasses** for plain data containers; Pydantic models for validated I/O.
- **ABCs** for all interfaces and repository contracts.
- **`pathlib.Path`** instead of `os.path`.
- **Async-first** for I/O-bound operations.
- **Composition over inheritance** — prefer protocols and dependency injection.

### Architecture Rules

- Pipeline stages contain **orchestration only** — no business logic.
- Business logic lives in **command/query handlers**.
- Handlers access the domain via **repository interfaces** (not concrete implementations).
- Cross-cutting concerns (logging, metrics) are handled by **infrastructure adapters**, not domain code.
- No circular imports. Enforce with `ruff` and `mypy`.

---

## Testing

- Place unit tests in `tests/unit/`.
- Place integration tests (requiring external services) in `tests/integration/`.
- Place end-to-end tests in `tests/e2e/`.
- Mark tests with `@pytest.mark.unit`, `@pytest.mark.integration`, or `@pytest.mark.e2e`.
- Aim for ≥ 80 % coverage on the `application/` and `domain/` packages.

---

## Questions?

Open a GitHub Discussion or contact the team via the project's communication channel.
