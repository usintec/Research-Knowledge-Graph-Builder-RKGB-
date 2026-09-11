# RKGB local infrastructure

Stage 2 provides a local dependency topology for the shared platform libraries:

| Service | Host endpoint | Purpose |
| --- | --- | --- |
| Kafka | `localhost:29092` | Event backbone |
| PostgreSQL + pgvector | `localhost:5432` | Relational service-owned data and vector foundations |
| Neo4j | `bolt://localhost:7687` / `http://localhost:7474` | Graph persistence foundation |
| Redis | `localhost:6379` | Cache, locks, and short-lived state |
| MinIO | `http://localhost:9000` / console `http://localhost:9001` | S3-compatible object storage |

## Start the dependencies

```bash
cp .env.example .env
docker compose -f infrastructure/docker-compose.yml config
docker compose -f infrastructure/docker-compose.yml up -d
docker compose -f infrastructure/docker-compose.yml ps
```

The MinIO init container creates the private `MINIO_BUCKET` bucket. Documents and
other large payloads belong in object storage and must be referenced by ID in
Kafka events; credentials and tokens must never be placed in event data.

## Stop and reset

```bash
docker compose -f infrastructure/docker-compose.yml down
# Add -v only when intentionally deleting local dependency data.
```

## Shared library entry points

- `@rkgb/common`: validated environment values, errors, health checks, and readiness primitives.
- `@rkgb/events`: versioned event envelope, safety validation, and serialization.
- `@rkgb/kafka`: client configuration, topic conventions, producer/consumer lifecycle,
  retries/DLQ hooks, and idempotency support.
- `@rkgb/database`: PostgreSQL migrations, Neo4j/Redis/MinIO clients, and health foundations.
- `@rkgb/observability`: correlation/trace metadata propagation and structured log primitives.

Runtime clients are constructed without opening network connections. Call `connect()`
from the service composition root and `close()` during graceful shutdown.
