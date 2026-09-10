# RKGB V1 Platform

This repository contains the NestJS/TypeScript platform foundation for the Research Knowledge
Graph Builder (RKGB). The platform is intentionally being built in stages. Existing research
implementation code must remain alongside this workspace and must not be migrated or deleted
without an explicit decision.

## Requirements

- Node.js 20+
- pnpm 10+

## Development

```bash
pnpm install
pnpm verify
pnpm --filter @rkgb/api-gateway start:dev
```

Every application exposes `GET /health` and `GET /ready`. The default port is `3000`; set `PORT`
and `SERVICE_NAME` in the environment to run another service locally.

## Workspace layout

- `apps/` — independently buildable NestJS applications
- `libs/` — shared platform libraries
- `infrastructure/` — local infrastructure configuration (added in later stages)
- `deploy/` — deployment manifests (added in later stages)
- `docs/platform/` — implementation notes for the platform foundation

Stage 1 deliberately contains no business workflows, Kafka consumers, persistence, identity
provider, model gateway, or agent behavior. Those belong to later stages.
