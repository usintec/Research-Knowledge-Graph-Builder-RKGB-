# Stage 3 — Identity, API Gateway & Session

## Prompt

```text
Implement Stage 3.

Build:
1. api-gateway
2. identity-service
3. session-service

NestJS/TypeScript only.

Identity:
- integrate with an OIDC provider such as Keycloak;
- do not implement an OIDC provider from scratch;
- validate JWTs at the platform boundary;
- establish stable user identity;
- roles/permissions;
- service identity distinct from human identity;
- tenant identity where applicable.

API Gateway:
- external REST API;
- authentication guard;
- authorization hooks;
- correlation IDs;
- request validation;
- rate-limit foundation;
- consistent errors;
- OpenAPI;
- routing to internal services.

Session service:
- sessions;
- conversations;
- ownership;
- timestamps;
- lifecycle;
- references to agent runs.

Explicitly separate:
User
Session
Conversation
AgentRun
AgentState
Context

Use PostgreSQL for owned state.

Events:
identity.user.created
identity.user.updated
session.created
session.closed
conversation.created
conversation.closed

Never publish raw JWTs to Kafka.

Tests:
- JWT validation;
- authorization failure;
- ownership isolation;
- session creation;
- conversation creation;
- event publication;
- API Gateway integration.
```
