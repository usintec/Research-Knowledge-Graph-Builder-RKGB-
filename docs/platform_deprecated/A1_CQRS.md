# Research Knowledge Graph Builder (RKGB)

# Application Layer Specification

## Document A1 — Command Bus, Query Bus & CQRS-lite Architecture

**Version:** 1.0

---

# 1. Purpose

The Application Layer coordinates business use cases within the RKGB platform.

It provides a lightweight Command Query Responsibility Segregation (CQRS-lite) architecture that separates state-changing operations (Commands) from read-only operations (Queries) without introducing distributed complexity.

The Application Layer is responsible for orchestrating business workflows while remaining independent of presentation, persistence, and infrastructure concerns.

---

# 2. Position in the Architecture

```text
Presentation Layer
(API, CLI, Pipelines, Agents, Kafka)

            │
            ▼

     Application Layer

            │
   ┌────────┴────────┐
   ▼                 ▼
Command Bus      Query Bus
   │                 │
   ▼                 ▼
Command Handler  Query Handler
   │                 │
   └────────┬────────┘
            ▼
        Domain Layer
            ▼
    Repository Layer
            ▼
   Infrastructure Layer
```

The Application Layer acts as the orchestration boundary for all business use cases.

---

# 3. Core Components

The Application Layer consists of:

* Commands
* Command Handlers
* Queries
* Query Handlers
* Command Bus
* Query Bus
* Application Events
* Middleware
* Dispatcher
* Result Objects

Each component has a single responsibility.

---

# 4. Commands

A Command represents an intention to change system state.

Examples include:

* ValidateDocumentCommand
* StoreDocumentCommand
* RegisterDocumentCommand
* BuildKnowledgeGraphCommand
* GenerateEmbeddingsCommand

Commands are immutable and contain only the data required to perform the operation.

---

# 5. Command Handlers

Each command has exactly one handler.

The handler:

* Validates business rules
* Coordinates domain services
* Persists aggregates
* Produces domain events
* Returns a command result

Handlers contain application orchestration but not infrastructure concerns.

---

# 6. Queries

A Query represents a request for information without modifying state.

Examples include:

* FindDuplicateQuery
* GetDocumentQuery
* SearchPapersQuery
* GetKnowledgeGraphQuery
* FindRelatedAuthorsQuery

Queries return DTOs or read models.

---

# 7. Query Handlers

Each query has exactly one handler.

Responsibilities include:

* Executing read operations
* Aggregating data from repositories
* Applying projections
* Returning optimized read models

Query handlers never modify domain state.

---

# 8. Command Bus

The Command Bus receives commands and routes them to the appropriate handler.

Responsibilities include:

* Handler resolution
* Middleware execution
* Logging
* Metrics
* Retry policies
* Exception translation

The Command Bus contains no business logic.

---

# 9. Query Bus

The Query Bus resolves and executes query handlers.

Responsibilities include:

* Handler resolution
* Caching (future)
* Read optimization
* Metrics
* Authorization middleware

Queries remain side-effect free.

---

# 10. Middleware

Middleware provides reusable cross-cutting behavior.

Examples include:

* Logging
* Authorization
* Validation
* Metrics
* Tracing
* Retry
* Transaction management

Middleware executes transparently around handlers.

---

# 11. Application Events

Handlers may publish application events after successful completion.

Examples include:

* DocumentUploaded
* GraphBuilt
* EmbeddingsGenerated

These events are distinct from domain events and are intended for workflow coordination.

---

# 12. Results

Handlers return strongly typed result objects.

Examples:

* ValidationResult
* RegistrationResult
* GraphBuildResult

Results avoid leaking domain entities to presentation layers.

---

# 13. Relationship to Pipelines

Pipeline stages do not invoke repositories or domain services directly.

Instead, they issue Commands and Queries through the appropriate buses.

This keeps stages thin and reusable.

---

# 14. Guiding Principle

The Application Layer is the orchestration boundary of RKGB.

By introducing Commands, Queries, Handlers, and Buses, the platform achieves loose coupling, reusable business use cases, centralized cross-cutting concerns, and a clean separation between execution workflows and domain logic.

This architecture enables the same business capability to be invoked consistently by pipelines, REST APIs, command-line tools, scheduled jobs, AI agents, or distributed workers without duplicating application logic.
