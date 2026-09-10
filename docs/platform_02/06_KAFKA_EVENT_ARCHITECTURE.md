# 06 — Kafka Event Architecture

## Kafka's role

Kafka is the platform's event backbone. It is responsible for durable event transport, fan-out, buffering, consumer isolation, replay and stream processing. It is not the source of truth for every domain entity.

## Topic families

### Identity

```text
identity.user.created
identity.user.updated
identity.user.deleted
```

### Documents

```text
document.uploaded
document.validated
document.processing.started
document.processing.completed
document.processing.failed
```

### Knowledge

```text
knowledge.entities.extracted
knowledge.relationships.extracted
knowledge.graph.updated
knowledge.index.updated
```

### Retrieval

```text
retrieval.requested
retrieval.completed
retrieval.failed
```

### Agents

```text
agent.task.created
agent.run.started
agent.run.completed
agent.run.failed
agent.tool.called
agent.tool.completed
```

### Models

```text
model.inference.requested
model.inference.completed
model.inference.failed
```

### Audit

```text
audit.event.created
```

## Consumer groups

A consumer group represents one logical processing function. For example:

```text
knowledge-extraction-workers
semantic-index-workers
analytics-workers
```

Multiple replicas in the same group share partitions; different groups independently consume the same event stream.

## Ordering

Ordering is guaranteed only within a Kafka partition. Events that require ordering must use a stable partition key such as `documentId`, `agentRunId` or another domain aggregate identifier.

## Delivery semantics

Consumers must be idempotent. At-least-once delivery is the default operational assumption. A duplicate event must not create duplicate graph nodes, duplicate embeddings or duplicate side effects.

## Retry and failure

Failed messages should use bounded retries and a dead-letter strategy. Consumers must distinguish transient failures from permanent validation failures.

## Kafka is not HTTP replacement

Use HTTP for interactive request/response. Use Kafka for asynchronous workflows, integration events, fan-out, background processing and event-driven projections.
