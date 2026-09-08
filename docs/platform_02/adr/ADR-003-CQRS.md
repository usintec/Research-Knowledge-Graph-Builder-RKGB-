# ADR-003 — Selective CQRS

**Status:** Accepted

## Decision

Apply CQRS selectively within services where separate command/query models provide a measurable architectural benefit.

## Rationale

CQRS is not a synonym for Kafka and is not required across the entire platform. The main candidates are document lifecycle, agent run state, projections and read-heavy research views.

Cross-service events may be carried by Kafka. The default consistency model is eventual consistency outside a service boundary.
