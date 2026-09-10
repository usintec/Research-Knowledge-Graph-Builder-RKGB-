# Stage 10 — Security, Observability & Production Hardening

## Prompt

```text
Implement Stage 10.

Harden the complete platform.

Observability:
- OpenTelemetry;
- distributed traces;
- traceId/correlationId;
- structured logs;
- Prometheus metrics;
- Grafana;
- Jaeger or compatible trace backend.

Trace:
Gateway
 -> Document
 -> Kafka
 -> Processing
 -> Extraction
 -> Graph/Vector
 -> Retrieval
 -> Agent
 -> Model Gateway
 -> Tool Service
 -> Response

Metrics:
- request count;
- error rate;
- latency;
- Kafka consumer lag;
- processing duration;
- retrieval latency;
- agent duration;
- model latency;
- token usage;
- tool calls;
- failed runs;
- document-processing failures.

Security:
- OIDC;
- RBAC;
- service-to-service authentication;
- tenant isolation;
- input validation;
- secrets management;
- TLS-ready configuration;
- least privilege;
- audit logging.

Kafka:
- bounded retries;
- DLQ;
- idempotent consumers;
- event versioning;
- operational metrics.

Data:
- PostgreSQL backup strategy;
- Neo4j backup strategy;
- object-storage backup strategy;
- Redis recovery expectations.

Containers:
- non-root;
- health/readiness probes;
- resource limits/requests;
- production Dockerfiles.

Kubernetes:
provide manifests or Helm structure for core services and dependencies.

CI:
- install;
- lint;
- type-check;
- unit tests;
- integration tests;
- build;
- container build.

Security tests:
- unauthorized access;
- cross-user access;
- tenant boundary;
- malformed event;
- invalid tool call;
- secret leakage.

Do not claim production-ready cloud deployment unless tested.
```
