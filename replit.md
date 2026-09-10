# RKGB V1 implementation notes

## Current baseline

The repository currently contains the RKGB V1 platform foundation described by Stage 0 and
Stage 1. No pre-existing application implementation was present when this baseline was created,
so no existing source was migrated or deleted.

The workspace uses NestJS and TypeScript for all applications. It contains 14 independently
buildable applications under `apps/` and 8 shared libraries under `libs/`. Stage 1 intentionally
does not implement business workflows, identity, persistence, Kafka integration, model access, or
agent behavior.

## Run locally

```bash
pnpm install
pnpm verify
pnpm --filter @rkgb/api-gateway start:dev
```

Applications default to port `3000`. Set `PORT` when running more than one service. Every current
application exposes:

- `GET /health` — process health
- `GET /ready` — readiness baseline

The `x-correlation-id` request header is propagated to the response; a UUID is generated when it
is absent. Logs are emitted as JSON records with the service name.

## Verification baseline

```bash
pnpm format:check
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

Infrastructure services and platform capabilities are intentionally deferred to the later stages
defined in `docs/rkgb-v1-development-plan/docs/development/`.
