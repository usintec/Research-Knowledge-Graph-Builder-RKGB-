# Stage 9 — Model Gateway & Governed Tool Execution

## Prompt

```text
Implement Stage 9.

Build:
- model-gateway-service
- tool-service

Model Gateway:
- provider abstraction;
- model registry metadata;
- routing;
- selection;
- timeout;
- retry;
- fallback;
- token usage;
- latency;
- cost;
- model version.

Support adapters for:
- OpenAI-compatible endpoints;
- Anthropic-compatible endpoints;
- vLLM/OpenAI-compatible endpoints;
- future providers through interfaces.

The Research Agent must not know provider-specific APIs.

Model request:
requestId
model
messages
tools
configuration
userId/tenantId where allowed
agentRunId
traceId

Model response:
response
model
provider
usage
latency
finishReason
requestId

Tool registry fields:
toolId
name
description
inputSchema
outputSchema
requiredPermissions
riskLevel
sideEffectClass
timeout
retryPolicy
enabled

Side-effect classes:
READ_ONLY
WRITE
EXTERNAL_ACTION
DESTRUCTIVE

LLM tool proposals are never automatically executable.
Validate schema, authorization, risk and policy before execution.

V1 tools should be safe:
- knowledge search;
- document lookup;
- graph lookup.

Avoid destructive/external-action tools in V1.

Audit every tool invocation.

Tests:
- provider adapter;
- timeout;
- retry;
- fallback;
- usage;
- authorization;
- schema validation;
- unauthorized tool;
- audit;
- idempotency.
```
