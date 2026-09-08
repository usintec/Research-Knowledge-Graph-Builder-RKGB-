# ADR-005 — OIDC Identity Boundary

**Status:** Accepted

## Decision

Use OpenID Connect/OAuth2 as the platform identity protocol. Start with a standards-compliant identity provider such as Keycloak and expose a NestJS identity-service for domain-level identity/access concerns.

## Rationale

Implementing an OIDC provider from scratch is unnecessary risk. A standards-based boundary allows the identity implementation to evolve without coupling every service to it.
