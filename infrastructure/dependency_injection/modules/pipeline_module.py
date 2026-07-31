"""Pipeline infrastructure registration module (placeholder — Step B+).

This module is the designated location for binding pipeline DSL abstractions
to their concrete implementations.

When Step B introduces the pipeline DSL, register components here::

    services.add_scoped(PipelineContext)
    services.add_singleton(IStageExecutor, DefaultStageExecutor)

No pipeline DSL components are registered yet.
"""

from __future__ import annotations

from infrastructure.dependency_injection.interfaces import IServiceCollection


class PipelineModule:
    """Registers pipeline DSL and stage infrastructure.

    **Current status:** placeholder — no registrations yet.

    Future registrations (Step B+):
        - ``PipelineContext`` (scoped — one per pipeline execution)
        - ``IStageExecutor`` → ``DefaultStageExecutor`` (singleton)
        - ``IPluginStageLoader`` → ``PluginStageLoader`` (singleton)

    Scope design:
        Pipeline execution contexts should be scoped services, created via
        ``provider.create_scope()`` at the start of each pipeline run and
        disposed at its completion. This isolates state between pipeline
        executions while sharing singleton infrastructure.
    """

    def register(self, services: IServiceCollection) -> None:  # noqa: ARG002
        """Register pipeline DSL services.

        Args:
            services: The service collection to register into.
        """
        # No implementations yet.
        # Registrations will be added here in Step B.
