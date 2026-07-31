"""Application layer registration module (CQRS placeholder — Step A5+).

This module reserves the registration slots for the Command Bus, Query Bus,
and Event Bus so that application-layer handlers can already declare those
abstractions as constructor dependencies before the buses are implemented.

When Step A5 introduces concrete bus implementations, replace the placeholder
comments with real registrations::

    services.add_singleton(ICommandBus, InMemoryCommandBus)
    services.add_singleton(IQueryBus,   InMemoryQueryBus)
    services.add_singleton(IEventBus,   InMemoryEventBus)

**Important constraints from the prompt:**
    - Do NOT implement the Command Bus, Query Bus, or Event Bus here.
    - Only prepare the registration infrastructure.
    - Concrete bus implementations belong to Step A5.
"""

from __future__ import annotations

from infrastructure.dependency_injection.interfaces import IServiceCollection


class ApplicationModule:
    """Registers CQRS infrastructure slots for the application layer.

    **Current status:** placeholder — no registrations yet.

    Future registrations (Step A5):
        - ``ICommandBus`` → ``InMemoryCommandBus``
        - ``IQueryBus`` → ``InMemoryQueryBus``
        - ``IEventBus`` → ``InMemoryEventBus``

    Handler registration (Step A5+):
        Command handlers, query handlers, and event subscribers will be
        discovered automatically via :class:`~..discovery.ServiceDiscovery`
        and registered as transient services::

            discovery = ServiceDiscovery()
            discovery.scan_package("application.command_handlers", services)
            discovery.scan_package("application.query_handlers", services)

    Extension points:
        The composition root exposes ``extra_modules`` so that feature teams
        and plugins can register their own handlers without modifying this
        module::

            provider = bootstrap_container(
                config, logging,
                extra_modules=[MyFeatureModule()],
            )
    """

    def register(self, services: IServiceCollection) -> None:  # noqa: ARG002
        """Register CQRS bus and handler services.

        Args:
            services: The service collection to register into.
        """
        # CQRS buses are not implemented in this step.
        # Slots are reserved; concrete implementations added in Step A5.
        #
        # Step A5 additions:
        #   services.add_singleton(ICommandBus, InMemoryCommandBus)
        #   services.add_singleton(IQueryBus, InMemoryQueryBus)
        #   services.add_singleton(IEventBus, InMemoryEventBus)
        #
        # Handler auto-discovery (Step A5):
        #   discovery = ServiceDiscovery()
        #   discovery.scan_package("application.command_handlers", services)
        #   discovery.scan_package("application.query_handlers", services)
