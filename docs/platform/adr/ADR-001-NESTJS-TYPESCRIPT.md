# ADR-001 — NestJS and TypeScript as the Default Service Stack

**Status:** Accepted

## Decision

Use NestJS and TypeScript as the default framework/language for RKGB application services.

## Rationale

- strong modular architecture;
- dependency injection;
- decorators and OOP-friendly design;
- native TypeScript ecosystem;
- Kafka and microservice support;
- good fit for REST APIs and platform services;
- shared contracts and types across services.

Specialized Python services remain permitted when ML/data tooling provides a material advantage. Such services communicate through APIs/events and do not change the primary platform stack.
