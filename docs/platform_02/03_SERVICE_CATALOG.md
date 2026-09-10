# 03 — Service Catalog

## Platform and experience services

| Service | Technology | Responsibility | Primary communication |
|---|---|---|---|
| `api-gateway` | NestJS/TS | External API, routing, rate limits, correlation | HTTP |
| `identity-service` | NestJS/TS | User profile, roles, permissions, tenant identity, IdP integration | HTTP + events |
| `session-service` | NestJS/TS | Sessions, conversations, run metadata | HTTP + events |

## Research data services

| Service | Responsibility |
|---|---|
| `document-service` | Uploads, metadata, versions, lifecycle, object references |
| `document-processing-service` | Parsing, text extraction, sectioning, chunking, metadata normalization |
| `knowledge-extraction-service` | NER, entities, relations, methods, datasets, citations, findings |
| `knowledge-graph-service` | Neo4j persistence and graph query interface |
| `semantic-index-service` | Embeddings, pgvector indexing, vector metadata |
| `retrieval-service` | Graph/vector retrieval, fusion, reranking, evidence sets |

## Agent and AI services

| Service | Responsibility |
|---|---|
| `agent-orchestrator-service` | LangGraph runs, state loading, context, routing, checkpoints |
| `agent-worker-service` | Specialized agent workers and asynchronous tasks |
| `model-gateway-service` | Provider/model abstraction, routing, token/cost accounting, fallback |
| `tool-service` | Tool registry, invocation, policy checks, execution and result normalization |
| `audit-service` | Immutable audit events and compliance-oriented records |

## Infrastructure services

Kafka, PostgreSQL, Neo4j, Redis and object storage are infrastructure dependencies rather than domain applications.

## Service ownership rule

Each service owns its domain state. Other services must use its API or published events rather than directly reading another service's private database tables.

## Initial V1 services to implement

Start with:

1. `api-gateway`
2. `identity-service`
3. `session-service`
4. `document-service`
5. `document-processing-service`
6. `knowledge-extraction-service`
7. `knowledge-graph-service`
8. `semantic-index-service`
9. `retrieval-service`
10. `agent-orchestrator-service`
11. `model-gateway-service`
12. `audit-service`

`agent-worker-service` and `tool-service` can start as modules inside the orchestrator and be extracted once their scaling/security boundary is justified.
