"""Processing Engine registration module (placeholder — Step B+).

This module is the designated location for binding Processing Engine
abstractions to their concrete implementations.

When Step B introduces the Pipeline Manager, Stage Registry, and associated
infrastructure, register them here::

    services.add_singleton(IPipelineManager, PipelineManager)
    services.add_singleton(IStageRegistry, StageRegistry)
    services.add_singleton(IExecutionPlanner, ExecutionPlanner)
    services.add_singleton(ICheckpointManager, CheckpointManager)
    services.add_singleton(IEventPublisher, EventPublisher)

No pipeline components are registered yet because the Processing Engine is
not implemented at this step.
"""

from __future__ import annotations

from infrastructure.dependency_injection.interfaces import IServiceCollection


class ProcessingModule:
    """Registers the Processing Engine infrastructure as singletons.

    **Current status:** placeholder — no registrations yet.

    Future registrations (Step B+):
        - ``IPipelineManager`` → ``PipelineManager``
        - ``IStageRegistry`` → ``StageRegistry``
        - ``IExecutionPlanner`` → ``ExecutionPlanner``
        - ``ICheckpointManager`` → ``CheckpointManager``
        - ``IEventPublisher`` → ``EventPublisher``

    No pipeline component may instantiate infrastructure objects — all
    dependencies must be received through the DI container.
    """

    def register(self, services: IServiceCollection) -> None:  # noqa: ARG002
        """Register processing engine services.

        Args:
            services: The service collection to register into.
        """
        # No implementations yet.
        # Registrations will be added here in Step B once the Processing
        # Engine is implemented.
