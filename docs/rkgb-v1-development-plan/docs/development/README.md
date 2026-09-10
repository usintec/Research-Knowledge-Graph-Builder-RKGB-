# RKGB V1 — Staged Development & AI Coding-Agent Prompts

This package converts the RKGB V1 multi-agent architecture into an executable, staged development plan.

## Non-negotiable technology direction

- **NestJS + TypeScript** for all application services
- Node.js
- pnpm monorepo
- REST/OpenAPI
- Apache Kafka + NestJS Kafka/KafkaJS
- PostgreSQL + pgvector
- Neo4j
- Redis
- MinIO/S3-compatible object storage
- OIDC/Keycloak
- LangGraph.js/TypeScript
- Docker
- Kubernetes
- Terraform
- OpenTelemetry + Prometheus + Grafana + Jaeger

**No Python application services in V1.**

The existing Python RKGB implementation is preserved. The new platform is developed alongside it.

## Stages

| Stage | Name | Main outcome |
|---|---|---|
| 0 | Development Contract & Baseline | Safe coding-agent boundary |
| 1 | NestJS Monorepo Foundation | Buildable multi-app workspace |
| 2 | Infrastructure & Shared Libraries | Kafka, DBs, storage and common contracts |
| 3 | Identity, Gateway & Session | Authenticated platform entry point |
| 4 | Document Ingestion | Upload, metadata and lifecycle |
| 5 | Processing & Extraction | Text, chunks, entities and relationships |
| 6 | Graph + Semantic Index | Neo4j + pgvector |
| 7 | Hybrid Retrieval | Graph/vector evidence retrieval |
| 8 | Agent Orchestration | LangGraph.js Research Agent |
| 9 | Model + Tool Gateway | Provider abstraction and governed tools |
| 10 | Security + Observability + Hardening | Operational V1 |
| 11 | Acceptance & Reference Demo | Full end-to-end proof |

## Execution rule

Give **one stage prompt at a time** to the coding agent.

For every stage the agent must:
1. inspect the repository;
2. preserve existing functionality;
3. implement only the requested stage;
4. add tests;
5. run lint/type-check/test/build;
6. update documentation;
7. report files changed and verification results;
8. identify unresolved issues.

## Final V1 flow

```text
Client
  -> API Gateway
  -> Identity/Session
  -> Document
  -> Processing
  -> Knowledge Extraction
  -> Neo4j + pgvector
  -> Hybrid Retrieval
  -> LangGraph Research Agent
  -> Model Gateway
  -> Governed Tools
  -> Evidence-grounded Response
  -> Audit + Trace + Metrics
```

Kafka is the asynchronous event backbone. HTTP remains appropriate for synchronous interactive operations.

## Architecture rules

- Each service owns its data.
- No direct cross-service database mutation.
- Kafka events use versioned contracts.
- Consumers are idempotent.
- Do not publish JWTs, secrets or binary documents to Kafka.
- Large payloads go to object storage and are referenced by ID.
- Identity, session, conversation, agent run, agent state and retrieval context remain separate.
- CQRS is selective, not mandatory everywhere.
- The Research Agent accesses retrieval through the Retrieval Service.
- Agents access models only through the Model Gateway.
- LLM-proposed tools are never automatically executable.

## Official references

- NestJS: https://docs.nestjs.com/
- NestJS Microservices: https://docs.nestjs.com/microservices/basics
- NestJS Kafka: https://docs.nestjs.com/microservices/kafka
- Apache Kafka: https://kafka.apache.org/documentation/
- LangGraph.js: https://langchain-ai.github.io/langgraphjs/
