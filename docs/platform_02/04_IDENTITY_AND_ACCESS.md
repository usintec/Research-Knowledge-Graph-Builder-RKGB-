# 04 — Identity and Access

## 1. Identity model

RKGB distinguishes four identities:

```text
User Identity      -> who the human is
Service Identity   -> which application is calling
Agent Identity     -> which agent/run is acting
Tenant Identity    -> which organizational boundary owns the data
```

These must not be collapsed into one `user_id` field.

## 2. Authentication

Use OpenID Connect for user authentication and OAuth 2.0 access tokens for API authorization. The initial implementation should use a standards-compliant identity provider such as Keycloak rather than implementing an OIDC server from scratch in NestJS.

The NestJS `identity-service` owns platform identity concerns such as:

- user profile;
- application roles;
- permissions;
- tenant membership;
- consent metadata;
- identity-provider integration;
- user lifecycle events.

## 3. Service-to-service identity

Services authenticate independently. A request such as:

```text
agent-orchestrator -> retrieval-service
```

must establish the identity of `agent-orchestrator`; it must not rely solely on the original user's JWT.

Use OAuth2 client credentials, workload identity and/or mTLS according to deployment maturity.

## 4. Request context

The gateway establishes a request context containing, where applicable:

```json
{
  "userId": "user-123",
  "tenantId": "tenant-001",
  "sessionId": "session-456",
  "conversationId": "conversation-789",
  "correlationId": "corr-abc",
  "traceId": "trace-def"
}
```

Only the minimum required fields should cross service boundaries.

## 5. Kafka identity propagation

Business identity belongs in the event payload when consumers need it. Trace and correlation information belongs in event metadata/headers and may also be included in the standard envelope.

Do not publish raw access tokens or full JWTs into Kafka topics.

## 6. Authorization

Authorization should be enforced at multiple boundaries:

```text
Gateway -> coarse API authorization
Service -> domain authorization
Tool Router -> action authorization
Data Store -> tenant/data isolation
```

Principle: authenticate once, authorize at every sensitive boundary.
