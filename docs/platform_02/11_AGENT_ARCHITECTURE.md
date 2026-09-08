# 11 — Agent Architecture

## V1: one research agent, multi-agent-ready platform

The first implementation should avoid premature agent proliferation. The orchestrator should support a graph of nodes and tools so specialized agents can be introduced later.

```text
User Question
     |
     v
Query Analyzer
     |
     v
Retrieval Planner
     |
     v
Hybrid Retrieval
     |
     v
Context / Evidence Builder
     |
     v
LLM Reasoner
     |
     +----> Tool Router ----> Tool/Model
     |
     v
Answer / Result
     |
     v
State + Audit
```

## LangGraph responsibilities

LangGraph should own run-level orchestration concerns such as:

- graph execution;
- branching;
- retries where appropriate;
- checkpoints;
- state transitions;
- human approval nodes where introduced;
- parallel independent branches.

NestJS owns the service boundary, authentication, API contracts, dependency injection, lifecycle and integration with Kafka/other services.

## Future multi-agent topology

```text
                  Agent Orchestrator
                         |
          +--------------+--------------+
          |              |              |
    Research Agent   Citation Agent   KG Agent
          |              |              |
          +--------------+--------------+
                         |
                    Shared Tools
                         |
               Retrieval / Model / Data
```

Agents should communicate through explicit tasks/events and structured outputs, not unrestricted prompt-to-prompt coupling.

## Agent run identity

Each execution has:

```text
runId
agentId
userId
sessionId
conversationId
parentRunId (optional)
traceId
status
startedAt
completedAt
```

## Human-in-the-loop

Actions that create external side effects should support an approval state:

```text
PLANNED -> AWAITING_APPROVAL -> APPROVED -> EXECUTING -> COMPLETED
```
