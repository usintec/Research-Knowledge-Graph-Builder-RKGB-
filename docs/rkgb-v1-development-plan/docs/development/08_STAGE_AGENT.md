# Stage 8 — LangGraph.js Research Agent

## Prompt

```text
Implement Stage 8.

Build agent-orchestrator-service using LangGraph.js/TypeScript.

Do not use Python LangGraph.

V1 contains one production-quality Research Agent but must remain multi-agent-ready.

Graph:

START
 -> Query Analyzer
 -> Retrieval Planner
 -> Hybrid Retrieval
 -> Evidence/Context Builder
 -> LLM Reasoner
 -> Tool Router if required
 -> Answer/Result
 -> Persist State + Audit
 -> END

LangGraph owns graph execution and state transitions.
NestJS owns service/API/auth/Kafka/persistence/lifecycle.

Agent run:
runId
agentId
userId
sessionId
conversationId
parentRunId optional
traceId
status
startedAt
completedAt

State:
- request;
- plan;
- evidence;
- tool results;
- model output;
- errors;
- approval state.

Statuses:
PLANNED
AWAITING_APPROVAL
APPROVED
EXECUTING
COMPLETED
FAILED
CANCELLED

Support checkpoints/resumability where practical.

The agent must call Retrieval Service, not Neo4j/pgvector directly.
The agent must call Model Gateway, not a provider directly.
No arbitrary tool execution.

Events:
agent.task.created
agent.run.started
agent.run.completed
agent.run.failed
agent.run.cancelled
agent.tool.called
agent.tool.completed

Long-running runs should be executable asynchronously through Kafka while the API returns a runId.

Tests:
- graph transitions;
- state schema;
- success;
- retrieval failure;
- model failure;
- resume;
- cancellation;
- event emission;
- authorization;
- trace propagation.

Output must contain evidence references.
```
