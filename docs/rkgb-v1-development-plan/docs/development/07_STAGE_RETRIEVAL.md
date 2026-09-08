# Stage 7 — Hybrid Retrieval

## Prompt

```text
Implement Stage 7.

Build retrieval-service.

Responsibilities:
1. query analysis;
2. retrieval planning;
3. vector candidate retrieval;
4. graph candidate retrieval;
5. candidate fusion;
6. optional reranking;
7. evidence-set construction.

Vector-first:
question -> embedding -> pgvector -> chunks

Graph-first:
question -> entities -> Neo4j traversal -> related knowledge/chunks

Prefer parallel graph/vector retrieval.

Evidence item:
documentId
chunkId
score
retrievalSource
graphPath
pageNumber
section
snippet
metadata
provenance

Initial configurable score:
S = α(vectorScore) + β(graphScore) + γ(sourceScore) + δ(recencyScore)

Do not claim the weights are optimal. Make the strategy replaceable.

Support:
- topK;
- filters;
- tenant restrictions;
- document restrictions;
- confidence thresholds.

The service must preserve provenance.

Expose:
- REST API;
- internal application interface;
- latency/candidate/evidence telemetry.

Tests:
- vector-only;
- graph-only;
- hybrid;
- empty results;
- duplicate fusion;
- authorization;
- provenance;
- deterministic scoring.
```
