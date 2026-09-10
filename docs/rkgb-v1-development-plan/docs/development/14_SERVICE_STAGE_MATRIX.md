# Service-to-Stage Matrix

| Service | Stage | Responsibility |
|---|---:|---|
| api-gateway | 3 | External API |
| identity-service | 3 | Identity/auth integration |
| session-service | 3 | Sessions/conversations |
| document-service | 4 | Document lifecycle |
| document-processing-service | 5 | Parsing/chunking |
| knowledge-extraction-service | 5 | Research fact extraction |
| knowledge-graph-service | 6 | Neo4j |
| semantic-index-service | 6 | pgvector |
| retrieval-service | 7 | Hybrid retrieval |
| agent-orchestrator-service | 8 | LangGraph |
| agent-worker-service | 8 | Async agent work |
| model-gateway-service | 9 | Model abstraction |
| tool-service | 9 | Governed tools |
| audit-service | 9/10 | Audit/compliance |
