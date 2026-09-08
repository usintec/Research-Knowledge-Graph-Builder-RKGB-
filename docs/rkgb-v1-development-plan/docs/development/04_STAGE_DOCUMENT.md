# Stage 4 — Document Ingestion & Lifecycle

## Prompt

```text
Implement Stage 4.

Build document-service.

Responsibilities:
- document metadata;
- owner/tenant;
- upload lifecycle;
- versions;
- MIME type;
- checksum;
- object-storage reference;
- processing status;
- timestamps.

Use MinIO/S3-compatible storage for bytes.

The service must not perform heavy parsing itself.

APIs:
POST /documents
POST /documents/:id/content
GET /documents
GET /documents/:id
DELETE /documents/:id
POST /documents/:id/process

Validate:
- file type;
- size;
- checksum;
- ownership;
- lifecycle transitions.

Emit:
document.uploaded
document.validated
document.processing.started
document.processing.failed

Do not put document bytes into Kafka.
Publish references.

Use transactional-outbox design where necessary.

Consumers and commands must be idempotent.

Tests:
- creation;
- upload;
- checksum;
- object storage;
- lifecycle;
- authorization;
- duplicate upload;
- event publication;
- failure handling.
```
