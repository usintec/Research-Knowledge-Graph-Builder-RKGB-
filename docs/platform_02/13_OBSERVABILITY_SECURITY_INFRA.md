# 13 — Observability, Security and Infrastructure

## Observability

Use OpenTelemetry as the common instrumentation layer.

Track:

- request latency p50/p95/p99;
- Kafka consumer lag;
- throughput;
- success/failure rate;
- retrieval precision/quality metrics;
- model latency;
- token usage and estimated cost;
- tool success rate;
- agent run duration;
- hallucination/evaluation metrics where measured;
- user feedback;
- queue/task age.

Every request should carry correlation and trace identifiers across HTTP and Kafka boundaries.

## Logging

Use structured JSON logs. Logs should include:

```text
service
version
environment
traceId
correlationId
userId (when appropriate)
tenantId (when appropriate)
operation
status
durationMs
```

Do not log credentials, raw access tokens or unnecessary sensitive document content.

## Security

Minimum controls:

- OAuth2/OIDC;
- RBAC/ABAC as required;
- secret management;
- encryption in transit;
- encryption at rest;
- tenant isolation;
- input validation;
- rate limiting;
- audit logging;
- least-privilege service identities;
- dependency and container scanning.

## Infrastructure

```text
Terraform
   |
   +--> Cloud resources
   +--> Kubernetes

Kubernetes
   |
   +--> NestJS services
   +--> Kafka
   +--> PostgreSQL
   +--> Neo4j
   +--> Redis
   +--> Object storage
   +--> Observability stack
```

For local development, Docker Compose should provide the smallest practical equivalent.

## CI/CD

Pipeline stages:

```text
Lint -> Unit Test -> Integration Test -> Build -> Security Scan
     -> Container Build -> Contract Tests -> Deploy -> Smoke Test
```

## Kubernetes scaling

Scale stateless services horizontally. Kafka consumers scale through consumer-group replicas and partitioning. Stateful infrastructure should use managed services where appropriate in production.

## Disaster recovery

Backups are required for PostgreSQL, Neo4j and object storage. Kafka retention is not a substitute for domain backups.
