# Research Knowledge Graph Builder (RKGB)

# Application Layer Specification

## Document A2 — Application Layer Project Structure

**Version:** 1.0

---

# 1. Purpose

The Application Layer organizes the business use cases of the RKGB platform.

Rather than grouping code by technical concerns alone, the Application Layer is organized around business capabilities while implementing CQRS-lite internally.

This approach improves cohesion, scalability, discoverability, and maintainability.

---

# 2. Design Principles

The Application Layer follows these principles:

* Feature-first organization
* CQRS-lite
* Single Responsibility Principle
* Dependency Inversion
* Vertical Slice Architecture
* Domain-Driven Design alignment
* Pipeline compatibility

Each feature owns its commands, queries, handlers, DTOs, and results.

---

# 3. Position in the Architecture

```text
Presentation Layer
        │
        ▼
Application Layer
        │
        ▼
Domain Layer
        │
        ▼
Repository Layer
        │
        ▼
Infrastructure Layer
```

The Application Layer orchestrates business use cases without containing persistence or presentation logic.

---

# 4. Top-Level Structure

```text
application/

│
├── common/
│
├── document_management/
│
├── document_extraction/
│
├── knowledge_extraction/
│
├── entity_resolution/
│
├── ontology_mapping/
│
├── graph_construction/
│
├── graph_validation/
│
├── semantic_indexing/
│
├── graph_rag/
│
├── research_intelligence/
│
├── export/
│
└── maintenance/
```

Each directory represents one business capability.

---

# 5. Common Package

The `common` package contains shared application infrastructure.

```text
common/

├── buses/
├── dispatcher/
├── middleware/
├── exceptions/
├── interfaces/
├── decorators/
├── messages/
├── results/
└── utilities/
```

This package provides reusable components without introducing business dependencies.

---

# 6. Feature Package Template

Every feature follows the same internal structure.

```text
feature/

│
├── commands/
│
├── command_handlers/
│
├── queries/
│
├── query_handlers/
│
├── dto/
│
├── events/
│
├── results/
│
├── validators/
│
├── policies/
│
└── tests/
```

The template is applied consistently across all business capabilities.

---

# 7. Commands

The `commands` package contains immutable requests that modify system state.

Examples:

* ValidateDocumentCommand
* RegisterDocumentCommand
* BuildKnowledgeGraphCommand
* GenerateEmbeddingsCommand

Commands contain only the data required to perform a business operation.

---

# 8. Command Handlers

Each command has a dedicated handler.

Responsibilities include:

* Business orchestration
* Domain coordination
* Repository interaction
* Event creation
* Returning results

Handlers remain free of presentation concerns.

---

# 9. Queries

The `queries` package contains read-only requests.

Examples:

* GetDocumentQuery
* SearchPaperQuery
* FindDuplicateQuery
* GetKnowledgeGraphQuery

Queries do not modify application state.

---

# 10. Query Handlers

Query handlers produce optimized read models.

Responsibilities include:

* Aggregating repository data
* Applying filters
* Constructing DTOs
* Returning query results

They should remain side-effect free.

---

# 11. DTO Package

DTOs define the contract between the Application Layer and its consumers.

Examples:

* UploadDocumentRequest
* DocumentResponse
* DuplicateResult
* MetadataResponse

DTOs prevent leakage of internal domain entities.

---

# 12. Results

Result objects represent successful application outcomes.

Examples:

* ValidationResult
* RegistrationResult
* GraphConstructionResult

Results encapsulate business outcomes in a consistent manner.

---

# 13. Events

Application events notify other application components about completed use cases.

Examples:

* DocumentRegistered
* GraphBuilt
* SemanticIndexCreated

These events may trigger additional workflows or notifications.

---

# 14. Validators

Validators enforce application-level rules before handlers execute.

Examples:

* Upload validation
* Duplicate policy validation
* Required field validation

Validation failures are reported as application exceptions.

---

# 15. Policies

Policies encapsulate configurable business rules.

Examples:

* Duplicate document policy
* Maximum upload size
* Supported file formats
* Retry policy

Policies are injected into handlers rather than hard-coded.

---

# 16. Testing

Each feature contains dedicated tests.

Recommended structure:

```text
tests/

├── command_tests/
├── query_tests/
├── integration/
└── fixtures/
```

Feature-level testing ensures business capabilities remain independently verifiable.

---

# 17. Dependency Rules

The Application Layer may depend on:

* Domain Layer
* Repository interfaces
* Shared application infrastructure

It must not depend directly on:

* FastAPI
* Neo4j drivers
* Storage SDKs
* Infrastructure implementations

Infrastructure dependencies are injected through interfaces.

---

# 18. Relationship to Pipelines

Pipeline stages invoke commands and queries from the relevant feature package.

Example:

```text
DocumentValidationStage
        │
        ▼
ValidateDocumentCommand
        │
        ▼
ValidateDocumentHandler
```

This keeps pipeline stages lightweight and reusable.

---

# 19. Relationship to APIs

REST endpoints, CLI commands, scheduled jobs, Kafka consumers, and AI agents all interact with the Application Layer using the same commands and queries.

This provides a single implementation for each business capability regardless of the caller.

---

# 20. Future Growth

As the platform evolves, new business capabilities are added by introducing new feature packages rather than modifying existing ones.

Examples:

* Collaboration
* User Management
* Workflow Administration
* Ontology Governance
* Analytics
* Plugin Management

The overall project structure remains stable.

---

# 21. Guiding Principle

The Application Layer organizes business behavior around capabilities rather than technical concerns.

By combining Vertical Slice Architecture with CQRS-lite, RKGB achieves high cohesion, low coupling, and a scalable project structure where each feature owns its commands, queries, handlers, and application contracts while remaining aligned with the underlying domain model and processing pipelines.
