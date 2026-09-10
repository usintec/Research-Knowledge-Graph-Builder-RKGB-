# 12 — Model and Tool Gateway

## Model Gateway

Agents must not directly bind to a single LLM provider.

```text
Agent
  |
  v
Model Gateway
  |
  +--> OpenAI-compatible provider
  +--> Anthropic-compatible provider
  +--> vLLM
  +--> Ollama/local models
  +--> future providers
```

Responsibilities:

- provider abstraction;
- model routing;
- authentication/secrets;
- rate limiting;
- retries/fallbacks;
- token accounting;
- cost estimation;
- latency metrics;
- model metadata;
- request/response policy.

## Tool Gateway

Tools are capabilities, not arbitrary code execution.

```text
Agent
  -> Tool Router
  -> Policy / Authorization
  -> Tool Executor
  -> Result Normalizer
  -> Agent
```

Initial tools:

- hybrid research retrieval;
- graph query;
- document lookup;
- metadata search;
- citation lookup;
- controlled web/search connector when enabled.

Future tools can include Python analysis, experiment execution and external APIs.

## Safety boundary

Tool definitions must declare:

```text
name
version
input schema
output schema
required permissions
risk level
side-effect class
timeout
retry policy
```

No arbitrary tool should execute merely because an LLM generated its name.
