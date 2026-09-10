# 10 — Hybrid Retrieval

## Goal

Combine explicit relationships from Neo4j with semantic similarity from pgvector.

## Retrieval paths

### Graph-first

```text
Question
  -> entity/link detection
  -> Neo4j traversal
  -> related documents/chunks
```

Useful for questions such as:

- Which papers use U-Net?
- Which authors worked with a given institution?
- Which datasets are associated with an algorithm?

### Vector-first

```text
Question
  -> embedding
  -> pgvector similarity
  -> candidate chunks
```

Useful for semantic questions where exact graph relationships are unknown.

### Parallel hybrid

```text
                    Query
                    /   \
                   /     \
              Neo4j     pgvector
                |          |
             Graph      Semantic
           candidates   candidates
                \          /
                 \        /
                 Candidate Fusion
                       |
                    Re-ranking
                       |
                  Evidence Set
```

## Scoring

A configurable hybrid score may be represented as:

```text
S_hybrid = α S_vector + β S_graph + γ S_recency + δ S_source + ε S_user
```

The exact weights must be evaluated experimentally rather than hard-coded as universal truth.

## Evidence set

Retrieval should return structured evidence, not just text:

```json
{
  "chunkId": "chunk-123",
  "documentId": "doc-123",
  "score": 0.91,
  "graphPath": ["Algorithm:U-Net", "Dataset:BraTS"],
  "source": {
    "page": 4,
    "section": "Methods"
  }
}
```

This allows the agent to reason over evidence and produce citations/provenance in its final response.
