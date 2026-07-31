"""Repository registration module (placeholder — Step A5+).

This module is the designated location for binding domain repository
interfaces to their Neo4j (and other storage) implementations.

When Step A5 introduces concrete repository classes, register them here
following the pattern::

    services.add_singleton(IDocumentRepository, Neo4jDocumentRepository)
    services.add_singleton(IEntityRepository, Neo4jEntityRepository)
    services.add_singleton(IRelationRepository, Neo4jRelationRepository)

No concrete implementations are registered yet because the Neo4j
infrastructure layer is not implemented at this step.
"""

from __future__ import annotations

from infrastructure.dependency_injection.interfaces import IServiceCollection


class RepositoryModule:
    """Registers domain repository implementations as singletons.

    **Current status:** placeholder — no registrations yet.

    Future registrations (Step A5+):
        - ``IDocumentRepository`` → ``Neo4jDocumentRepository``
        - ``IEntityRepository`` → ``Neo4jEntityRepository``
        - ``IRelationRepository`` → ``Neo4jRelationRepository``
        - ``IKnowledgeGraphRepository`` → ``Neo4jKnowledgeGraphRepository``
    """

    def register(self, services: IServiceCollection) -> None:  # noqa: ARG002
        """Register repository bindings.

        Args:
            services: The service collection to register into.
        """
        # No concrete implementations yet.
        # Registrations will be added here in Step A5 once the Neo4j
        # infrastructure layer is implemented.
        #
        # Example (Step A5):
        #   services.add_singleton(IDocumentRepository, Neo4jDocumentRepository)
