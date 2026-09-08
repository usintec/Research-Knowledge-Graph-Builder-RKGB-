# Stage 2 — Infrastructure & Shared Platform Libraries

## Prompt

```text
Implement Stage 2 of RKGB V1.

Create local Docker Compose infrastructure for:
- Kafka;
- PostgreSQL;
- Neo4j;
- Redis;
- MinIO.

Create shared libraries for:
- Kafka configuration;
- event publishing/consuming;
- event envelope;
- correlation/trace metadata;
- configuration validation;
- database helpers;
- common errors;
- health/readiness;
- observability primitives.

Use this versioned event envelope:

eventId
eventType
eventVersion
occurredAt
producer
tenantId
actor
correlationId
traceId
aggregate
data

Kafka requirements:
- explicit client IDs;
- explicit consumer group IDs;
- topic naming conventions;
- event-based publishing;
- request-response only when justified;
- graceful lifecycle;
- retry/DLQ design;
- idempotency support.

Never place secrets, passwords, raw JWTs or large binary payloads in events.

PostgreSQL must have connection and migration foundations.
Neo4j must have driver and health foundations.
Redis must have connection and health foundations.
MinIO must have bucket/bootstrap documentation.

Add:
- Kafka producer/consumer smoke test;
- PostgreSQL health test;
- Neo4j health test;
- Redis health test;
- MinIO connectivity test;
- shared-library unit tests.

Do not implement research-domain schemas yet.
```
