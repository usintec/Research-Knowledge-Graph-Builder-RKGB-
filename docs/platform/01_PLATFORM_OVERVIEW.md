# 01 — Platform Overview

## 1. Purpose

RKGB is a Research Knowledge Graph and Multi-Agent Intelligence Platform. Its first product is a Research Knowledge Graph Builder that ingests scholarly documents, extracts structured knowledge, indexes semantic content, and provides evidence-grounded research assistance.

The platform is intentionally designed so that the research builder is the first domain, not the final architecture.

## 2. Evolution

```text
V1  Research Knowledge Builder
    Documents -> Processing -> Knowledge Graph + Vector Index -> Retrieval

V2  Research Agent
    Retrieval -> Evidence -> LLM reasoning -> grounded response

V3  Multi-Agent Research Platform
    Research Agent + Citation Agent + KG Agent + Analysis Agent + Writing Agent

V4  General Multi-Agent Platform
    Additional domains and agent families reuse the same identity, event,
    state, model, tool, security and observability infrastructure.
```

## 3. Architectural principles

1. **Service boundaries are explicit.** Major capabilities are independently deployable applications.
2. **NestJS + TypeScript is the default application stack.** Python remains available for specialized ML/data workers where it provides a material advantage.
3. **Kafka is the event backbone.** It connects services through durable, versioned events.
4. **CQRS is applied selectively.** It is a service-level pattern, not a requirement that every service have separate databases.
5. **Identity is centralized.** Users, service identities, tenants, sessions and agent runs are distinct concepts.
6. **Knowledge and retrieval are first-class services.** Agents consume retrieval capabilities instead of embedding storage logic inside prompts.
7. **Models are behind a gateway.** Agents do not couple directly to one provider or model runtime.
8. **Actions are policy-controlled.** Tools execute through an authorization and policy boundary.
9. **Everything important is observable.** Correlation IDs, trace IDs, metrics, structured logs and audit records are propagated end-to-end.
10. **Infrastructure is replaceable.** Local Docker Compose should be able to approximate the production topology; Kubernetes is the target deployment platform.

## 4. Technology baseline

| Concern | Initial technology |
|---|---|
| Application framework | NestJS |
| Language | TypeScript |
| Workspace | pnpm monorepo |
| API | REST/JSON; OpenAPI |
| Event backbone | Apache Kafka |
| Identity protocol | OAuth 2.0 / OpenID Connect |
| Identity provider | Keycloak-compatible; can be hosted alongside a NestJS identity service |
| Relational state | PostgreSQL |
| Graph | Neo4j |
| Vector store | PostgreSQL + pgvector |
| Cache / ephemeral state | Redis |
| Object storage | S3-compatible storage / MinIO locally |
| Agent orchestration | LangGraph.js |
| Model access | Model Gateway |
| Containers | Docker |
| Orchestration | Kubernetes |
| IaC | Terraform |
| Observability | OpenTelemetry + Prometheus + Grafana; Jaeger-compatible tracing |
| CI/CD | GitHub Actions or GitLab CI |

## 5. V1 scope

V1 supports:

- user authentication and authorization;
- document upload and lifecycle management;
- PDF/document text extraction;
- chunking and metadata creation;
- research entity and relationship extraction;
- Neo4j knowledge graph persistence;
- pgvector semantic indexing;
- graph, vector and hybrid retrieval;
- evidence/provenance tracking;
- one primary research agent orchestrated with LangGraph;
- model-provider abstraction;
- audit and observability.

Out of scope for the first vertical slice:

- autonomous long-running multi-agent swarms;
- arbitrary external side effects;
- production-scale model training;
- full enterprise multi-tenancy implementation;
- custom OIDC provider implementation from scratch.
