# RKGB Platform Documentation

## Research Knowledge Graph & Multi-Agent Intelligence Platform

RKGB evolves from a research knowledge graph builder into an event-driven, identity-aware, multi-agent platform. Version 1 remains focused on research literature ingestion, knowledge graph construction, hybrid retrieval, and evidence-grounded research assistance. Later versions can add additional agents and domains without replacing the platform foundation.

## Documentation map

| Document | Purpose |
|---|---|
| [01_PLATFORM_OVERVIEW.md](./01_PLATFORM_OVERVIEW.md) | Vision, principles, scope and evolution |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | Target architecture and end-to-end flow |
| [03_SERVICE_CATALOG.md](./03_SERVICE_CATALOG.md) | Independently deployable service boundaries |
| [04_IDENTITY_AND_ACCESS.md](./04_IDENTITY_AND_ACCESS.md) | User, service and agent identity |
| [05_SESSION_AND_STATE.md](./05_SESSION_AND_STATE.md) | Session, conversation, run and agent state |
| [06_KAFKA_EVENT_ARCHITECTURE.md](./06_KAFKA_EVENT_ARCHITECTURE.md) | Kafka topics, consumers and event flow |
| [07_EVENT_CONTRACTS.md](./07_EVENT_CONTRACTS.md) | Versioned event envelope and contracts |
| [08_CQRS_AND_CONSISTENCY.md](./08_CQRS_AND_CONSISTENCY.md) | CQRS, projections and consistency model |
| [09_RESEARCH_PIPELINE.md](./09_RESEARCH_PIPELINE.md) | RKGB document-to-knowledge workflow |
| [10_HYBRID_RETRIEVAL.md](./10_HYBRID_RETRIEVAL.md) | Neo4j + pgvector retrieval architecture |
| [11_AGENT_ARCHITECTURE.md](./11_AGENT_ARCHITECTURE.md) | LangGraph orchestration and multi-agent evolution |
| [12_MODEL_AND_TOOL_GATEWAY.md](./12_MODEL_AND_TOOL_GATEWAY.md) | Models, tools, policy and controlled execution |
| [13_OBSERVABILITY_SECURITY_INFRA.md](./13_OBSERVABILITY_SECURITY_INFRA.md) | Observability, security, Kubernetes and operations |
| [adr/](./adr/) | Architecture decision records |

## V1 implementation principle

The architecture defines all major platform boundaries, but implementation should begin with a thin vertical slice:

`Identity -> API Gateway -> Document -> Processing -> Extraction -> Neo4j/pgvector -> Retrieval -> Agent -> Model Gateway -> Response`

Kafka is introduced early as the event backbone, but not every operation must become asynchronous. Synchronous APIs are retained where an immediate request/response is appropriate.
