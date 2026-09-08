# Stage 0 — Development Contract & Repository Baseline

## Goal

Establish a safe contract for the AI coding agent before implementation begins.

## Prompt

```text
You are the principal engineer implementing RKGB V1, a multi-agent research intelligence platform.

The repository already contains a Research Knowledge Graph Builder implementation. Treat the existing implementation as protected. Do not delete, rewrite or migrate it unless explicitly instructed.

The new platform must be implemented with NestJS + TypeScript.

Technology constraints:
- NestJS
- TypeScript
- Node.js
- pnpm
- Kafka
- PostgreSQL
- pgvector
- Neo4j
- Redis
- MinIO/S3
- OIDC/Keycloak
- LangGraph.js
- Docker
- Kubernetes-ready configuration
- OpenTelemetry

Do not create Python application services.

Before coding:
1. inspect the entire repository structure;
2. identify package managers;
3. identify existing apps and tests;
4. identify Docker/CI configuration;
5. identify directories that conflict with the planned platform;
6. propose the smallest reversible change.

The new platform will eventually contain:
api-gateway
identity-service
session-service
document-service
document-processing-service
knowledge-extraction-service
knowledge-graph-service
semantic-index-service
retrieval-service
agent-orchestrator-service
agent-worker-service
tool-service
model-gateway-service
audit-service

Shared libraries:
common
contracts
events
kafka
identity
security
observability
database

Rules:
- HTTP for synchronous interactive operations.
- Kafka for asynchronous workflows, lifecycle events, fan-out and integration.
- Services own their persistence.
- No shared mutable tables across service boundaries.
- No raw JWTs/secrets in Kafka.
- No binary documents in Kafka.
- Consumers must be idempotent.
- No arbitrary LLM tool execution.
- Do not implement future-stage functionality early.

After any implementation:
- run formatter;
- lint;
- type-check;
- unit tests;
- build;
- integration tests where relevant;
- update documentation.

Return:
1. repository assessment;
2. conflicts;
3. recommended implementation boundary;
4. commands required to verify the baseline.
```

## Stage gate

No destructive migration is allowed.
