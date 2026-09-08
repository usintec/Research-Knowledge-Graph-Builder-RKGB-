# Stage Dependency Graph

```text
0 Baseline
   |
1 Monorepo
   |
2 Infrastructure
   |
   +----> 3 Identity/Gateway/Session
   |
   +----> 4 Document
              |
              v
          5 Processing/Extraction
              |
              v
          6 Neo4j + pgvector
              |
              v
          7 Hybrid Retrieval
              |
              v
          8 LangGraph Agent
              |
              v
          9 Model + Tools
              |
              v
         10 Hardening
              |
              v
         11 Acceptance
```

Parallel work becomes possible after Stage 2, but contracts must stabilize before downstream services are finalized.
