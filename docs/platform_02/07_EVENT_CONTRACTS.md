# 07 — Event Contracts

All Kafka events use a versioned envelope.

```json
{
  "eventId": "evt-01",
  "eventType": "document.uploaded",
  "eventVersion": 1,
  "occurredAt": "2026-09-08T12:00:00.000Z",
  "producer": "document-service",
  "tenantId": "tenant-001",
  "actor": {
    "type": "user",
    "id": "user-123"
  },
  "correlationId": "corr-01",
  "traceId": "trace-01",
  "aggregate": {
    "type": "document",
    "id": "doc-123"
  },
  "data": {}
}
```

## Rules

1. Event names describe facts and use past tense where practical.
2. Events are immutable after publication.
3. Event schemas are versioned.
4. Consumers must tolerate additive fields.
5. Breaking changes require a new event version or event type.
6. Do not put secrets, passwords, access tokens or unnecessary PII in events.
7. Event payloads should contain enough business context for the consumer to act without synchronous calls where appropriate.
8. Large files and documents are referenced by object-storage IDs rather than embedded into Kafka messages.

## Example

```json
{
  "eventType": "knowledge.entities.extracted",
  "eventVersion": 1,
  "aggregate": {
    "type": "document",
    "id": "doc-123"
  },
  "data": {
    "entities": [
      { "id": "e1", "type": "Algorithm", "name": "U-Net" },
      { "id": "e2", "type": "Dataset", "name": "BraTS" }
    ],
    "sourceChunkIds": ["chunk-1", "chunk-2"]
  }
}
```
