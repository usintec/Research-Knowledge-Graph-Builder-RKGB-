# Stage 02 — Infrastructure & Shared Platform Libraries

## Scope

Stage 02 establishes local infrastructure and reusable TypeScript libraries for
the platform. It does not implement document schemas, research pipelines,
repositories, retrieval, agents, or service business logic.

The existing Python RKGB implementation remains protected. The V1 platform is
implemented alongside it as a NestJS/TypeScript pnpm workspace.

## Local dependencies

`infrastructure/docker-compose.yml` provisions:

- Kafka in KRaft mode with internal and host listeners;
- PostgreSQL 16 with the pgvector image;
- Neo4j 5 community;
- Redis 7;
- MinIO plus a one-shot private bucket bootstrap container.

All services have container health checks. Host defaults and credentials are
documented in `.env.example`; they are development-only values and must be
replaced in deployed environments.

## Event contract

Events use the versioned `EventEnvelope<TData>` from `@rkgb/events`:

```ts
{
  eventId,
  eventType,
  eventVersion,
  occurredAt,
  producer,
  tenantId,
  actor,
  correlationId,
  traceId,
  aggregate,
  data
}
```

`createEventEnvelope()` validates required identifiers, actor and aggregate
references, timestamp, positive version, payload size, and forbidden credential
fields. Binary payloads and payloads larger than 1 MiB are rejected. Store
large documents in MinIO and place only an object reference in an event.

## Kafka conventions

`@rkgb/kafka` provides:

- `kafkaConfigFromEnv()` with explicit brokers, client ID, group ID, retry settings,
  and topic prefix;
- `buildTopicName()` using `rkgb.<domain>.<event>.v<version>`;
- `.retry` and `.dlq` topic helpers;
- `KafkaConnection` for explicit producer/consumer connect and graceful disconnect;
- `KafkaEventPublisher` for event-based publishing;
- `KafkaEventConsumer` with event-ID idempotency and failure/DLQ hooks;
- `InMemoryIdempotencyStore` as a test foundation and interface seam for a
  durable store in a later stage.

Kafka is used for asynchronous workflows, lifecycle events, fan-out, and
integration. Interactive request/response traffic remains HTTP. Raw JWTs,
secrets, credentials, and binary documents are prohibited from events.

## Persistence foundations

`@rkgb/database` exposes:

- `PostgresClient` for pooled SQL access and health probes;
- `MigrationRunner` with a protected `rkgb_schema_migrations` table and
  transactional `up()` migrations;
- `Neo4jClient` with driver connectivity and health checks;
- `RedisClient` with lazy connection, ping health, and graceful quit;
- `MinioObjectStorage` with bucket bootstrap and bucket health checks;
- environment-driven configuration for all four dependencies.

Each future service owns its own schema and migrations. Stage 02 does not create
research-domain tables or cross-service persistence.

## Health/readiness and observability

`HealthCheckRegistry` runs named dependency probes and returns a readiness report
that is `ready` only when every registered check is up. `@rkgb/observability`
provides `CorrelationContextStore`, HTTP header conversion helpers, and
structured JSON log records. The same correlation and trace metadata is carried
by HTTP headers and Kafka event fields.

## Verification

```bash
pnpm format:check
pnpm lint
pnpm typecheck
pnpm test
pnpm build
docker compose -f infrastructure/docker-compose.yml config
```

With Docker dependencies running, opt-in smoke tests with:

```bash
RUN_INFRA_SMOKE_TESTS=1 pnpm test -- --runInBand
```

The smoke tests are intentionally opt-in so normal unit-test runs remain
hermetic and do not require local Docker.