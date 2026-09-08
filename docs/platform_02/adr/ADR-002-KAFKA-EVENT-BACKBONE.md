# ADR-002 — Kafka as Event Backbone

**Status:** Accepted

## Decision

Use Apache Kafka for durable asynchronous events, fan-out, background processing and service integration.

## Rationale

The platform contains independently scalable document, extraction, indexing, agent and analytics workloads. Kafka provides a durable event log, consumer groups, replay and independent consumption.

RabbitMQ may be introduced for task/command workloads if a dedicated work-queue model becomes materially beneficial, but Kafka is the default event backbone.
