"""Infrastructure layer — concrete adapters for all external services.

This package provides implementations of domain repository interfaces
and infrastructure services (Neo4j, storage, cache, messaging, etc.).
It is the only layer permitted to depend on third-party libraries
for persistence, messaging, and external APIs.
"""
