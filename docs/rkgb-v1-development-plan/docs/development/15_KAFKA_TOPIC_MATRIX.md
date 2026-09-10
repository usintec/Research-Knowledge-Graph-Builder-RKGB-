# Kafka Topic Matrix

## Identity
identity.user.created
identity.user.updated
identity.user.deleted

## Session
session.created
session.closed
conversation.created
conversation.closed

## Document
document.uploaded
document.validated
document.processing.started
document.processing.completed
document.processing.failed

## Knowledge
knowledge.entities.extracted
knowledge.relationships.extracted
knowledge.graph.updated
knowledge.index.updated

## Retrieval
retrieval.requested
retrieval.completed
retrieval.failed

## Agent
agent.task.created
agent.run.started
agent.run.completed
agent.run.failed
agent.run.cancelled
agent.tool.called
agent.tool.completed

## Model
model.inference.requested
model.inference.completed
model.inference.failed

## Audit
audit.event.created

Partition by aggregate where ordering matters:
- documentId for document workflows;
- agentRunId for agent workflows;
- conversationId for conversation workflows.

Consumers must be idempotent.
