# ADR-006 — LangGraph for Agent Orchestration

**Status:** Accepted

## Decision

Use LangGraph.js inside the NestJS/TypeScript agent orchestration boundary for stateful agent workflows.

## Rationale

The platform requires explicit graph execution, branching, persistence/checkpoints and controlled tool invocation. LangGraph provides the orchestration model while NestJS remains responsible for the service boundary and platform integrations.
