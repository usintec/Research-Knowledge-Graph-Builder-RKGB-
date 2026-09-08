# ADR-004 — Neo4j + PostgreSQL/pgvector for Hybrid Retrieval

**Status:** Accepted

## Decision

Use Neo4j for explicit relationships and graph traversal, and PostgreSQL with pgvector for semantic vector retrieval.

## Rationale

Research knowledge contains both explicit relationships and semantic similarity. A hybrid retrieval service can combine both signals and preserve provenance.
