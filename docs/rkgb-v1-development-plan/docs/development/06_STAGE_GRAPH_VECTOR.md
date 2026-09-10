# Stage 6 — Knowledge Graph + Semantic Index

## Prompt

```text
Implement Stage 6.

Build:
- knowledge-graph-service
- semantic-index-service

Neo4j domain entities:
Document
Section
Chunk
Author
Institution
Researcher
Algorithm
Method
Dataset
Experiment
Finding
Keyword
Citation
ResearchTopic

Relationships:
AUTHORED_BY
AFFILIATED_WITH
CONTAINS
HAS_CHUNK
USES_METHOD
USES_ALGORITHM
USES_DATASET
REPORTS_FINDING
HAS_KEYWORD
CITES
RELATED_TO

Every fact must preserve:
documentId
chunkId
pageNumber where available
sourceTextHash
extractionMethod
confidence
extractedAt

Define graph constraints/indexes and version the graph schema.

pgvector records:
- chunkId;
- documentId;
- embedding;
- metadata;
- model name/version;
- dimensions;
- content hash;
- createdAt.

Embedding generation must be behind an interface and should later call the Model Gateway.

Implement stable content identity and idempotent indexing.

Events:
knowledge.graph.updated
knowledge.index.updated

Tests:
- graph persistence;
- relationship creation;
- provenance;
- duplicate prevention;
- vector insertion;
- similarity search;
- re-indexing;
- embedding version handling.

Do not implement hybrid retrieval yet.
```
