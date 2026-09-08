# Stage 1 — NestJS Monorepo & Platform Foundation

## Prompt

```text
Implement Stage 1 of RKGB V1.

Create a pnpm-based NestJS monorepo for the new platform while preserving the existing RKGB implementation.

Create:

apps/
  api-gateway/
  identity-service/
  session-service/
  document-service/
  document-processing-service/
  knowledge-extraction-service/
  knowledge-graph-service/
  semantic-index-service/
  retrieval-service/
  agent-orchestrator-service/
  agent-worker-service/
  tool-service/
  model-gateway-service/
  audit-service/

libs/
  common/
  contracts/
  events/
  kafka/
  identity/
  security/
  observability/
  database/

infrastructure/
deploy/
docs/platform/

All applications should initially be minimal and buildable. Do not fake future business functionality.

Establish:
- pnpm workspace;
- strict TypeScript;
- shared tsconfig;
- linting/formatting;
- environment configuration;
- health/readiness endpoints;
- graceful shutdown;
- structured logging foundation;
- common error format;
- correlation ID support;
- Docker build strategy;
- independent application builds.

Add representative unit/health tests.

Acceptance:
- pnpm install succeeds;
- all applications type-check;
- all applications build;
- tests pass;
- existing RKGB implementation remains untouched;
- no Python service is introduced.
```
