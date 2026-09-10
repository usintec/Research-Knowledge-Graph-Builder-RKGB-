# Stage 11 — V1 Acceptance & Reference Demo

## Prompt

```text
Implement Stage 11.

Do not introduce major new architecture. This stage proves and documents the existing platform.

Create an end-to-end acceptance scenario:

1. Start infrastructure.
2. Start NestJS services.
3. Authenticate test user.
4. Create session.
5. Create conversation.
6. Upload research paper.
7. Verify metadata.
8. Verify processing events.
9. Process paper.
10. Verify chunks.
11. Verify extracted entities/relationships.
12. Verify Neo4j graph.
13. Verify pgvector records.
14. Ask research question.
15. Verify hybrid retrieval.
16. Start Research Agent.
17. Verify LangGraph execution.
18. Verify Model Gateway.
19. Verify evidence-grounded response.
20. Verify run state.
21. Verify audit.
22. Verify distributed trace and metrics.

Create:
- E2E tests;
- smoke-test script;
- local demo script;
- architecture walkthrough;
- troubleshooting guide;
- service dependency map;
- event flow diagram;
- sequence diagram;
- V1 limitations;
- technical debt register.

Reference question:

"Which methods and datasets are used in the uploaded research papers, and how are they related?"

Expected:
- graph retrieval finds explicit relationships;
- vector retrieval finds semantic matches;
- evidence is returned with provenance;
- Research Agent synthesizes the answer;
- model is called through Model Gateway;
- run is persisted;
- audit is persisted;
- trace is available.

V1 is complete only when this workflow is reproducible from clean local infrastructure.
```
