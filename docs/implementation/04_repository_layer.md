# Research Knowledge Graph Builder (RKGB)

# Implementation Specification

## Document 04 — Repository Layer

**Version:** 1.0

---

# 1. Purpose

The Repository Layer provides a persistence abstraction for the RKGB platform.

Repositories expose aggregate-oriented interfaces that allow the application and domain layers to retrieve and persist business objects without depending on specific database technologies.

Repositories are responsible for:

* Aggregate persistence
* Aggregate retrieval
* Transaction participation
* Query execution
* Persistence mapping
* Concurrency coordination

Repositories are **not** responsible for business logic or workflow orchestration.

---

# 2. Position in the Architecture

```text
REST API
      │
      ▼
DTO Layer
      │
      ▼
Command / Query
      │
      ▼
Handler
      │
      ▼
Workflow
      │
      ▼
Application Service
      │
      ▼
Domain Service
      │
      ▼
Repository Interface
      │
      ▼
Infrastructure Repository
      │
      ▼
Storage Backend
```

The application depends only on repository interfaces.

---

# 3. Repository Philosophy

Repositories represent **collections of aggregates**, not database tables.

Example

The application asks for:

```
PaperRepository.get_by_doi(...)
```

not

```
SELECT * FROM papers ...
```

The repository determines how the aggregate is reconstructed.

---

# 4. Repository Categories

The platform defines five repository categories.

```text
Aggregate Repositories

↓

Graph Repositories

↓

Search Repositories

↓

Workflow Repositories

↓

Infrastructure Repositories
```

---

# 5. Aggregate Repositories

Aggregate repositories persist domain aggregates.

Examples

```text
ManagedDocumentRepository

PaperRepository

AuthorRepository

InstitutionRepository

DatasetRepository

AlgorithmRepository

KnowledgeGraphRepository
```

Each repository owns one aggregate root.

---

# 6. Repository Interfaces

Repository interfaces belong to the **Domain Layer**.

Example location

```text
app/
└── domain/
    └── publication/
        └── repositories/
            └── paper_repository.py
```

The interface contains only business-oriented operations.

---

# 7. Repository Implementations

Concrete implementations belong to the **Infrastructure Layer**.

Example

```text
app/
└── infrastructure/
    └── persistence/
        ├── neo4j/
        ├── postgres/
        ├── sqlite/
        └── filesystem/
```

Infrastructure classes implement the domain interfaces.

---

# 8. Aggregate Ownership

Each aggregate has one primary repository.

| Aggregate       | Repository                |
| --------------- | ------------------------- |
| ManagedDocument | ManagedDocumentRepository |
| Paper           | PaperRepository           |
| Author          | AuthorRepository          |
| Institution     | InstitutionRepository     |
| Dataset         | DatasetRepository         |
| Algorithm       | AlgorithmRepository       |
| KnowledgeGraph  | KnowledgeGraphRepository  |

Repositories should not overlap ownership.

---

# 9. Polyglot Persistence

Different repositories use different storage technologies.

| Aggregate           | Primary Storage     |
| ------------------- | ------------------- |
| ManagedDocument     | PostgreSQL / SQLite |
| DocumentVersion     | PostgreSQL / SQLite |
| ProcessingHistory   | PostgreSQL / SQLite |
| Paper               | Neo4j               |
| Author              | Neo4j               |
| Institution         | Neo4j               |
| Dataset             | Neo4j               |
| Algorithm           | Neo4j               |
| Citation            | Neo4j               |
| KnowledgeGraph      | Neo4j               |
| Uploaded PDF        | File Storage        |
| Embeddings (future) | Vector Database     |
| Cache (future)      | Redis               |

The application is unaware of the underlying storage engine.

---

# 10. Repository Responsibilities

Repositories may:

* Save aggregates
* Retrieve aggregates
* Delete aggregates
* Search aggregates
* Load relationships
* Execute transactions
* Rehydrate domain objects

Repositories must not:

* Execute workflows
* Perform NLP
* Build graphs
* Validate business rules
* Publish domain events

---

# 11. Query Specifications

Complex filtering is expressed through specifications rather than ad hoc methods.

Examples

```text
PaperByDOISpecification

PaperByAuthorSpecification

PaperByKeywordSpecification

DuplicateDocumentSpecification

RecentPublicationsSpecification
```

Repositories accept specifications and translate them into database queries.

---

# 12. Repository Lifecycle

```text
Application Service
        │
        ▼
Repository Interface
        │
        ▼
Infrastructure Repository
        │
        ▼
Persistence Mapper
        │
        ▼
Database
```

Retrieval follows the reverse path, reconstructing aggregates before returning them.

---

# 13. Persistence Mapping

Repositories use mappers to convert between:

```text
Domain Aggregate

⇄

Persistence Model
```

Persistence models may differ from domain models.

This keeps the domain independent of storage schemas.

---

# 14. Unit of Work

Repositories participate in a Unit of Work.

Responsibilities

* Track aggregate changes
* Coordinate transactions
* Commit changes atomically
* Roll back on failure

Example

```text
Workflow

↓

Application Service

↓

UnitOfWork

↓

Repositories

↓

Commit
```

A Unit of Work may span multiple repositories.

---

# 15. Transaction Boundaries

A transaction begins when a business use case starts and ends when all repository operations complete successfully.

Example

```text
Upload Document

↓

Save Document Metadata

↓

Create Processing Record

↓

Commit
```

Graph construction and file storage may require compensating actions where distributed transactions are not available.

---

# 16. Neo4j Repository

The Neo4j repository is responsible for graph persistence.

Capabilities

* Create nodes
* Create relationships
* Merge nodes
* Execute Cypher
* Traverse graphs
* Apply constraints
* Manage indexes

The repository hides Cypher details from the domain.

---

# 17. Relational Repository

The relational repository manages operational data.

Examples

* Document metadata
* Processing history
* Workflow execution
* Configuration
* User preferences (future)

This storage is optimized for transactional consistency.

---

# 18. File Repository

The file repository manages binary assets.

Examples

* Uploaded PDFs
* Exported RDF
* OWL files
* Reports
* Generated artifacts

Responsibilities

* Save
* Retrieve
* Delete
* Version
* Verify integrity

---

# 19. Future Vector Repository

Phase 2 introduces semantic embeddings.

Capabilities

* Store vectors
* Delete vectors
* Similarity search
* Metadata filtering
* Hybrid retrieval

The interface remains independent of the chosen vector database.

---

# 20. Future Cache Repository

Redis-based repositories may cache:

* Search results
* Graph summaries
* Ontology lookups
* Frequently accessed papers

Caching remains transparent to the application layer.

---

# 21. Error Handling

Repositories translate infrastructure failures into repository-specific exceptions.

Examples

* RepositoryUnavailableException
* AggregateNotFoundException
* ConcurrencyConflictException
* PersistenceException

Infrastructure-specific exceptions should not propagate into the domain.

---

# 22. Repository Naming

Repositories should be named after the aggregate they manage.

Examples

* PaperRepository
* AuthorRepository
* ManagedDocumentRepository

Avoid names such as:

* DatabaseManager
* Neo4jHelper
* SQLUtility

Repository names should express business ownership.

---

# 23. Repository Collaboration

```text
Application Service
      │
      ├────────────► ManagedDocumentRepository
      ├────────────► PaperRepository
      ├────────────► AuthorRepository
      ├────────────► KnowledgeGraphRepository
      └────────────► ProcessingRepository
```

Each repository focuses on its own aggregate.

---

# 24. Testing Strategy

Repository interfaces are tested with mock implementations.

Infrastructure repositories are validated through integration tests against real databases.

This separation allows business logic to be tested without requiring Neo4j or PostgreSQL.

---

# 25. Future Evolution

The repository layer is designed to support:

Phase 2

* Vector repositories
* Embedding repositories

Phase 3

* Agent memory repositories

Phase 4

* Graph embedding repositories
* Recommendation repositories

Phase 5

* Distributed repositories
* Event-sourced projections
* Data lake connectors

New storage technologies should be introduced by implementing repository interfaces rather than modifying domain code.

---

# 26. Guiding Principle

Repositories are the persistence gateway of the RKGB platform.

They expose business-oriented operations over aggregates, conceal storage technologies, participate in transactional consistency, and enable the domain model to remain independent of databases, graph engines, file systems, and future infrastructure.

By treating repositories as aggregate collections rather than database wrappers, the platform remains maintainable, testable, and adaptable as it evolves into a production-grade AI Research Intelligence Platform.
