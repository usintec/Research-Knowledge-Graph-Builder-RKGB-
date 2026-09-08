# 08 — CQRS and Consistency

## Principle

CQRS separates command responsibilities from query responsibilities. It is not a requirement that the entire RKGB platform use separate databases.

```text
Command -> Write Model -> State Change -> Event -> Projection -> Read Model

Query  -> Read Model
```

## Where CQRS is useful

Use CQRS when a service has:

- substantially different write and read models;
- high read fan-out;
- projections that can be rebuilt;
- asynchronous processing;
- audit/history requirements;
- independently scalable query workloads.

## Example: document service

```text
UploadDocumentCommand
       |
       v
 Document Write Model
       |
       v
 PostgreSQL
       |
       v
 document.uploaded
       |
      Kafka
       |
       v
 Document Read Projection
```

## Kafka and CQRS

They solve different problems:

```text
CQRS  = architectural separation of commands and queries
Kafka  = event transport and durable event streaming
```

Kafka can carry the events between a write side and projections, but CQRS can exist without Kafka and Kafka can exist without CQRS.

## Consistency

The default cross-service consistency model is **eventual consistency**.

Strong transactional consistency is reserved for operations that truly require it inside one service boundary. Cross-service distributed transactions should not be the default design.

## Idempotency

Every event consumer must be safe to retry. Use an inbox/idempotency record where side effects are non-trivial.

## Outbox pattern

When a service must atomically persist state and publish an event, use a transactional outbox:

```text
DB Transaction
  |
  +--> domain state
  +--> outbox event

Outbox Publisher
  |
  v
Kafka
```

This avoids the dual-write failure where the database succeeds but event publication fails.
