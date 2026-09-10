# Coding-Agent Checklist

## Before coding
- [ ] Read the stage prompt.
- [ ] Inspect repository.
- [ ] Inspect previous-stage output.
- [ ] Identify affected apps/libs.
- [ ] Confirm no destructive migration.
- [ ] Confirm contracts.

## During coding
- [ ] NestJS/TypeScript only.
- [ ] Preserve service ownership.
- [ ] No cross-service DB mutation.
- [ ] Validate inputs.
- [ ] No hard-coded secrets.
- [ ] Add tests.
- [ ] Preserve correlation/trace context.
- [ ] Idempotent Kafka consumers.
- [ ] Document decisions.

## After coding

```bash
pnpm install
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

For infrastructure:

```bash
docker compose config
docker compose up -d
docker compose ps
```

For E2E:

```bash
pnpm test:e2e
```

## Final report

### Implemented
### Files changed
### Tests
### Build
### Infrastructure
### Known limitations
### Deferred to later stages
### Architectural decisions

## Forbidden

- Do not overwrite the existing Python RKGB implementation.
- Do not introduce Python microservices.
- Do not replace Kafka with RabbitMQ.
- Do not put provider calls directly in the agent.
- Do not allow arbitrary shell/code execution.
- Do not put JWTs/secrets/binary documents in Kafka.
- Do not claim untested features are production-ready.
- Do not implement all stages in one pass.
