# Stage 5 — Document Processing & Knowledge Extraction

## Prompt

```text
Implement Stage 5.

Build:
- document-processing-service
- knowledge-extraction-service

All application code must be NestJS/TypeScript.

Document processing:
- retrieve object from storage;
- parse PDF/DOCX where supported;
- extract text;
- preserve page numbers;
- detect sections;
- detect references/citations;
- create chunks;
- preserve provenance.

Parser implementations must use adapters/interfaces.

Chunk metadata:
documentId
chunkId
pageNumber
section
text
textHash
sequence
sourceReference

Knowledge extraction:
- authors;
- institutions;
- methods;
- algorithms;
- datasets;
- findings;
- keywords;
- citations;
- research topics;
- relationships.

Use provider interfaces for extraction models. Do not hard-code one provider.

Events:
document.processing.completed
document.processing.failed
knowledge.entities.extracted
knowledge.relationships.extracted

Every extracted fact must preserve confidence and provenance.

Consumers must be idempotent.

Do not write to another service's database.

Tests:
- parser adapters;
- chunking;
- provenance;
- schema validation;
- idempotency;
- retry/failure;
- document -> chunks -> extraction integration.
```
