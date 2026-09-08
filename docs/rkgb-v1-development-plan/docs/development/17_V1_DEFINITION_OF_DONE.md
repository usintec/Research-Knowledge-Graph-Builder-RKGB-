# RKGB V1 Definition of Done

## Platform
- [ ] NestJS/TypeScript monorepo.
- [ ] Existing RKGB preserved.
- [ ] Service ownership documented.
- [ ] Shared contracts.
- [ ] Kafka event backbone.

## Research pipeline
- [ ] Document upload.
- [ ] Object storage.
- [ ] Processing.
- [ ] Chunking with provenance.
- [ ] Entity extraction.
- [ ] Relationship extraction.
- [ ] Neo4j persistence.
- [ ] pgvector indexing.

## Retrieval
- [ ] Vector retrieval.
- [ ] Graph retrieval.
- [ ] Hybrid retrieval.
- [ ] Evidence provenance.
- [ ] Authorization/tenant filtering.

## Agent
- [ ] LangGraph.js Research Agent.
- [ ] Persistent run metadata.
- [ ] Recoverable state.
- [ ] Evidence-grounded answer.

## Models
- [ ] Model Gateway.
- [ ] Provider adapters.
- [ ] Usage tracking.
- [ ] Retry/fallback.
- [ ] No provider coupling in agents.

## Tools
- [ ] Registry.
- [ ] Schemas.
- [ ] Permissions.
- [ ] Risk classes.
- [ ] Audit.

## Operations
- [ ] Docker local environment.
- [ ] CI.
- [ ] Health/readiness.
- [ ] OpenTelemetry.
- [ ] Metrics.
- [ ] Structured logs.
- [ ] Kubernetes deployment structure.
- [ ] Backup/recovery documentation.

## Security
- [ ] OIDC.
- [ ] RBAC.
- [ ] Tenant isolation.
- [ ] Secrets management.
- [ ] No credentials in Kafka.
- [ ] No arbitrary agent execution.

## Demo
Authenticate -> Session -> Upload -> Process -> Extract -> Graph/Vector -> Hybrid Retrieval -> Research Agent -> Model Gateway -> Evidence-grounded answer -> Audit -> Trace.
