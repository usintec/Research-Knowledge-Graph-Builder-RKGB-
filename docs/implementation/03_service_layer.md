# Research Knowledge Graph Builder (RKGB)

# Implementation Specification

## Document 03 — Service Layer

**Version:** 1.0

---

# 1. Purpose

The Service Layer coordinates the execution of business use cases within the RKGB platform.

It acts as the bridge between external interfaces (REST APIs, CLI tools, event handlers) and the domain model.

The Service Layer is responsible for:

* Executing business workflows
* Coordinating multiple domain entities
* Managing transactions
* Publishing domain events
* Invoking repositories
* Delegating business rules to domain services

The Service Layer should **never** contain infrastructure-specific logic.

---

# 2. Layer Architecture

```text
Client
    │
    ▼
REST API
    │
    ▼
Application Services
    │
    ▼
Domain Services
    │
    ▼
Repositories
    │
    ▼
Infrastructure
```

Responsibilities are clearly separated.

---

# 3. Service Categories

The platform defines four categories of services.

```text
Application Services

↓

Domain Services

↓

Infrastructure Services

↓

Cross-Cutting Services
```

Each category has a distinct responsibility.

---

# 4. Application Services

Application Services orchestrate complete business use cases.

They:

* Receive requests
* Validate input
* Coordinate domain objects
* Call repositories
* Publish events
* Return results

They do **not** implement business rules themselves.

---

# 5. Application Service Catalogue

## DocumentApplicationService

Responsibilities

* Upload document
* Retrieve document
* Archive document
* Replace document
* Delete document

Collaborators

* ManagedDocument
* DocumentRepository
* ValidationService
* StorageService
* EventPublisher

---

## PaperApplicationService

Responsibilities

* Create Paper
* Update metadata
* Manage citations
* Retrieve publications

Collaborators

* Paper
* PaperRepository
* CitationService

---

## GraphApplicationService

Responsibilities

* Build knowledge graph
* Merge graphs
* Validate graph
* Export graph

Collaborators

* KnowledgeGraph
* GraphBuilderService
* GraphRepository

---

## SearchApplicationService

Responsibilities

* Keyword search
* Semantic search
* Graph traversal
* Hybrid retrieval

Collaborators

* SearchService
* EmbeddingService
* GraphRepository

---

## OntologyApplicationService

Responsibilities

* Load ontology
* Validate entities
* Apply semantic mappings
* Resolve ontology versions

---

# 6. Domain Services

Domain Services encapsulate business logic that spans multiple entities.

They are stateless and reusable.

---

## DocumentValidationService

Business Responsibilities

* Validate PDF format
* Validate MIME type
* Validate checksum
* Validate document policy

Inputs

ManagedDocument

Outputs

ValidationResult

---

## DuplicateDetectionService

Responsibilities

* Compare checksums
* Compare metadata
* Compare semantic similarity
* Identify duplicates

Future Enhancement

Embedding-based duplicate detection.

---

## MetadataExtractionService

Responsibilities

* Extract embedded metadata
* Normalize metadata
* Populate DocumentMetadata

---

## VersionResolutionService

Responsibilities

* Determine whether upload is:

  * New document
  * Updated version
  * Duplicate

---

## PaperExtractionService

Responsibilities

Generate a Paper aggregate from a processed document.

Extract:

* Title
* Abstract
* Keywords
* Authors
* DOI

---

## CitationResolutionService

Responsibilities

* Resolve citation targets
* Link referenced papers
* Detect unresolved citations

---

## AuthorResolutionService

Responsibilities

Merge duplicate authors using:

* ORCID
* Name similarity
* Affiliation
* Email

---

## InstitutionResolutionService

Responsibilities

Normalize institutional names.

Examples

MIT

↓

Massachusetts Institute of Technology

---

## KnowledgeGraphConstructionService

Responsibilities

Transform domain entities into graph objects.

Creates:

Nodes

Relationships

Graph metadata

---

## GraphValidationService

Responsibilities

Validate:

* Broken relationships
* Duplicate nodes
* Missing properties
* Invalid ontology mappings

---

## OntologyValidationService

Responsibilities

Ensure extracted knowledge conforms to ontology rules.

Examples

Algorithm

cannot

TRAINED_ON

Journal

---

## SemanticNormalizationService

Responsibilities

Normalize terminology.

Examples

UNet

↓

U-Net

Dice Similarity Coefficient

↓

Dice Score

---

# 7. Infrastructure Services

Infrastructure Services wrap external technologies.

Examples

PDFParserService

Neo4jService

EmbeddingService

StorageService

KafkaService (future)

EmailService (future)

They contain no business logic.

---

# 8. Cross-Cutting Services

These services support the entire platform.

Examples

LoggingService

ConfigurationService

MetricsService

AuditService

HealthCheckService

NotificationService

TracingService

CorrelationIdService

---

# 9. Service Dependencies

```text
Application Service

│

├── Domain Service

├── Repository

├── Event Publisher

└── Domain Model
```

Application Services coordinate but do not own business rules.

---

# 10. Service Interaction Example

Uploading a document.

```text
Upload API

↓

DocumentApplicationService

↓

DocumentValidationService

↓

DuplicateDetectionService

↓

VersionResolutionService

↓

StorageService

↓

DocumentRepository

↓

Publish DocumentUploaded Event
```

Each service has one responsibility.

---

# 11. Graph Construction Workflow

```text
Paper

↓

PaperExtractionService

↓

SemanticNormalizationService

↓

OntologyValidationService

↓

KnowledgeGraphConstructionService

↓

GraphValidationService

↓

KnowledgeGraphRepository
```

Each step is replaceable.

---

# 12. Search Workflow

```text
Search Request

↓

SearchApplicationService

↓

EmbeddingService

↓

GraphRepository

↓

RankingService

↓

Search Results
```

Supports:

* Keyword search
* Semantic search
* Hybrid retrieval

---

# 13. Event Publication

Application Services publish events after successful business operations.

Examples

DocumentUploaded

DocumentValidated

PaperExtracted

GraphBuilt

OntologyValidated

GraphExported

Application Services never dispatch events directly.

They publish through the Event Bus.

---

# 14. Transaction Boundaries

Each Application Service defines a transaction boundary.

Examples

Upload Document

Transaction begins

↓

Validation

↓

Storage

↓

Repository Update

↓

Event Publication

↓

Transaction commits

If any critical step fails, the transaction is rolled back where applicable, and compensating actions are triggered for non-transactional resources (such as file storage).

---

# 15. Error Handling

Errors are classified into:

Business Errors

* Duplicate Document
* Invalid Citation
* Ontology Violation

Infrastructure Errors

* Database Unavailable
* Storage Failure
* Neo4j Connection Error

Business errors remain in the domain layer.

Infrastructure errors are translated before reaching the application layer.

---

# 16. Service Naming Convention

Services follow capability-based naming.

Examples

DocumentApplicationService

KnowledgeGraphConstructionService

SemanticNormalizationService

DuplicateDetectionService

Avoid generic names such as:

Manager

Helper

Processor

Utility

Service names should describe a clear business capability.

---

# 17. Future Service Expansion

As the platform evolves, new services will be introduced without modifying existing contracts.

Examples

Phase 2

* NamedEntityRecognitionService
* RelationExtractionService
* TopicModelingService
* EmbeddingGenerationService

Phase 3

* AgentPlanningService
* ToolExecutionService
* MemoryManagementService
* ResearchAssistantService

Phase 4

* GraphEmbeddingService
* LinkPredictionService
* RecommendationService

Phase 5

* KafkaPublishingService
* SparkProcessingService
* AirflowOrchestrationService
* FeatureStoreService
* ModelMonitoringService

This follows the Open/Closed Principle.

---

# 18. Service Collaboration Diagram

```text
REST API
    │
    ▼
DocumentApplicationService
    │
    ├───────────────► DocumentValidationService
    │
    ├───────────────► DuplicateDetectionService
    │
    ├───────────────► VersionResolutionService
    │
    ├───────────────► StorageService
    │
    ├───────────────► DocumentRepository
    │
    └───────────────► EventPublisher

PaperApplicationService
    │
    ├───────────────► PaperExtractionService
    ├───────────────► AuthorResolutionService
    ├───────────────► CitationResolutionService
    └───────────────► PaperRepository

GraphApplicationService
    │
    ├───────────────► SemanticNormalizationService
    ├───────────────► OntologyValidationService
    ├───────────────► KnowledgeGraphConstructionService
    ├───────────────► GraphValidationService
    └───────────────► KnowledgeGraphRepository
```

---

# 19. Guiding Principle

Services represent business capabilities—not technical utilities.

Application Services orchestrate use cases.

Domain Services encapsulate reusable business rules.

Infrastructure Services isolate external technologies.

By maintaining this separation, the RKGB platform remains modular, testable, and adaptable as it evolves into a full AI Research Intelligence Platform with semantic search, GraphRAG, Agentic AI, Graph Machine Learning, and distributed event-driven processing.
