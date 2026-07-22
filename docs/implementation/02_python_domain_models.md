# Research Knowledge Graph Builder (RKGB)

# Implementation Specification

## Document 02 — Python Domain Models

**Version:** 1.0

---

# 1. Purpose

This document defines the Python domain model for the RKGB platform.

The domain model represents the business concepts identified in the Domain Model Specification and serves as the central abstraction for the application.

These classes are independent of:

* FastAPI
* Neo4j
* SQLite/PostgreSQL
* PDF libraries
* spaCy
* Hugging Face
* NetworkX

The domain layer contains business behavior, not infrastructure concerns.

---

# 2. Design Principles

The domain model follows:

* Domain-Driven Design (DDD)
* Clean Architecture
* SOLID Principles
* Rich Domain Model
* Composition over Inheritance
* Explicit Aggregates
* Immutable Value Objects

---

# 3. Package Structure

```text
app/
└── domain/
    ├── common/
    ├── document/
    ├── publication/
    ├── people/
    ├── organization/
    ├── dataset/
    ├── algorithm/
    ├── experiment/
    ├── graph/
    └── ontology/
```

Each package contains:

```text
entities/
value_objects/
repositories/
services/
events/
factories/
policies/
exceptions/
```

---

# 4. Base Types

Every domain model derives from one of three categories.

## Entity

Represents an object with identity.

Examples:

* Paper
* Author
* Dataset
* ManagedDocument

Characteristics:

* Unique identifier
* Mutable lifecycle
* Equality based on identity

---

## Value Object

Represents descriptive information without identity.

Examples:

* DOI
* EmailAddress
* ORCID
* FileChecksum
* FileSize
* StoragePath
* PublicationYear

Characteristics:

* Immutable
* Equality based on value
* No independent lifecycle

---

## Aggregate Root

Controls access to a group of related entities.

Aggregate roots include:

* ManagedDocument
* Paper
* Author

Child objects are modified only through the aggregate root.

---

# 5. Document Aggregate

## Aggregate Root

ManagedDocument

Responsibilities:

* Represents an uploaded file
* Controls document lifecycle
* Owns metadata and versions
* Coordinates processing status

Attributes:

* document_id
* filename
* original_filename
* mime_type
* status
* checksum
* created_at
* updated_at

Relationships:

```text
ManagedDocument

├── DocumentMetadata

├── DocumentVersion

├── StorageLocation

└── ProcessingHistory
```

Behavior:

* validate()
* add_version()
* archive()
* update_status()
* mark_processed()

---

## DocumentMetadata

Value Object

Attributes:

* title
* author
* producer
* creation_date
* modification_date
* page_count
* language
* pdf_version

Immutable after creation.

---

## DocumentVersion

Entity

Attributes:

* version_number
* checksum
* uploaded_at
* notes

Behavior:

* supersede()
* compare()

---

## StorageLocation

Value Object

Attributes:

* relative_path
* absolute_path
* storage_backend
* file_size

Behavior:

* resolve_path()

---

# 6. Publication Aggregate

## Aggregate Root

Paper

Represents a scientific publication.

Attributes:

* paper_id
* title
* abstract
* doi
* publication_year
* publication_date
* language
* keywords

Relationships:

```text
Paper

├── Authors

├── Journal

├── Conference

├── Citations

├── Datasets

├── Algorithms

├── Methods

├── Metrics

└── Research Areas
```

Behavior:

* add_author()
* add_dataset()
* add_algorithm()
* add_metric()
* cite()
* add_keyword()

---

## Citation

Entity

Attributes:

* citation_id
* context
* section
* position

Behavior:

* link_target()
* validate()

---

## Keyword

Value Object

Attributes:

* value
* normalized_value

---

# 7. People Aggregate

## Aggregate Root

Author

Attributes:

* author_id
* full_name
* email
* orcid
* affiliations
* research_interests

Behavior:

* add_affiliation()
* add_publication()
* merge_duplicate()

---

## Institution

Entity

Attributes:

* institution_id
* name
* country
* city
* website

Behavior:

* register_author()
* update_details()

---

# 8. Research Aggregate

## Dataset

Entity

Attributes:

* dataset_id
* name
* source
* version
* license
* modality

Behavior:

* add_paper()
* update_version()

---

## Algorithm

Entity

Attributes:

* algorithm_id
* name
* family
* description

Behavior:

* train_on()
* solve_task()
* implement_method()

---

## Method

Entity

Attributes:

* method_id
* name
* description

Behavior:

* classify()

---

## Task

Entity

Attributes:

* task_id
* name
* description

Behavior:

* add_metric()

---

## Metric

Entity

Attributes:

* metric_id
* name
* value
* unit

Behavior:

* validate_value()

---

## Disease

Entity

Attributes:

* disease_id
* name
* ontology_code

Behavior:

* normalize()

---

## ResearchArea

Entity

Attributes:

* area_id
* name
* description

Behavior:

* classify_paper()

---

# 9. Graph Aggregate

## GraphNode

Represents a node before persistence.

Attributes:

* node_id
* label
* properties

Behavior:

* add_property()
* validate()

---

## GraphRelationship

Represents an edge.

Attributes:

* relationship_id
* type
* source
* target
* properties

Behavior:

* validate()

---

## KnowledgeGraph

Aggregate Root

Attributes:

* graph_id
* nodes
* relationships

Behavior:

* add_node()
* add_relationship()
* merge()
* validate()
* export()

---

# 10. Processing Aggregate

## ProcessingContext

Represents execution state.

Attributes:

* pipeline_id
* current_stage
* correlation_id
* started_at
* completed_at

Behavior:

* advance()
* fail()
* complete()

---

## ProcessingResult

Value Object

Attributes:

* success
* warnings
* errors
* execution_time

---

# 11. Domain Events

Each aggregate publishes domain events.

Examples:

ManagedDocument

* DocumentUploaded
* DocumentValidated
* DocumentArchived

Paper

* PaperCreated
* CitationAdded

KnowledgeGraph

* GraphBuilt
* GraphValidated

Events represent business facts and are consumed by the application layer.

---

# 12. Factories

Complex aggregates are created through factories.

Examples:

* ManagedDocumentFactory
* PaperFactory
* KnowledgeGraphFactory
* AuthorFactory

Factories ensure objects are created in a valid state.

---

# 13. Repositories

Repositories abstract persistence.

Interfaces only exist in the domain layer.

Examples:

* ManagedDocumentRepository
* PaperRepository
* AuthorRepository
* DatasetRepository
* KnowledgeGraphRepository

Implementations belong in the infrastructure layer.

---

# 14. Policies

Policies encapsulate business rules.

Examples:

* DuplicateDetectionPolicy
* DocumentValidationPolicy
* CitationValidationPolicy
* AuthorMergePolicy

Policies avoid scattering business logic across entities.

---

# 15. Exceptions

Domain-specific exceptions include:

* InvalidDocumentException
* DuplicateDocumentException
* InvalidCitationException
* InvalidOntologyException
* GraphValidationException

Domain exceptions should not expose infrastructure details.

---

# 16. Relationships Between Aggregates

```text
ManagedDocument
        │
GENERATES
        ▼
Paper
   │
   ├── WRITTEN_BY ─────────► Author
   │                         │
   │                         └── AFFILIATED_WITH ─► Institution
   │
   ├── USES ───────────────► Dataset
   │
   ├── USES ───────────────► Algorithm
   │                         │
   │                         └── IMPLEMENTS ─────► Method
   │
   ├── REPORTS ────────────► Metric
   │
   ├── STUDIES ────────────► Disease
   │
   ├── BELONGS_TO ─────────► ResearchArea
   │
   └── CITES ──────────────► Paper

Paper
        │
GENERATES
        ▼
KnowledgeGraph
```

---

# 17. Lifecycle Summary

```text
PDF Upload
     │
     ▼
ManagedDocument
     │
Validation
     │
Metadata Extraction
     │
Paper
     │
NLP Enrichment
     │
KnowledgeGraph
     │
Neo4j Persistence
```

Each aggregate evolves independently while preserving clear ownership boundaries.

---

# 18. Mapping to Other Layers

| Domain Model      | Infrastructure Representation |
| ----------------- | ----------------------------- |
| ManagedDocument   | File storage + metadata table |
| Paper             | Neo4j `:Paper` node           |
| Author            | Neo4j `:Author` node          |
| Dataset           | Neo4j `:Dataset` node         |
| Algorithm         | Neo4j `:Algorithm` node       |
| KnowledgeGraph    | Neo4j graph + RDF export      |
| ProcessingContext | Pipeline execution state      |

The domain model remains persistence-agnostic.

---

# 19. Guiding Principle

The Python domain model is the canonical in-memory representation of the RKGB platform.

Every service, pipeline stage, repository, API endpoint, event, and graph operation must interact through these domain models rather than directly manipulating infrastructure-specific objects. This ensures that business rules remain centralized, testable, and independent of frameworks or storage technologies.
