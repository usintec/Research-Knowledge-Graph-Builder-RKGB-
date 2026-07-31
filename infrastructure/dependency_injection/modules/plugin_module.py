"""Plugin system registration module (placeholder).

This module is the designated location for binding the Plugin Registry and
plugin loader infrastructure to the DI container.

Plugins extend the platform through well-defined extension points:
    * Register services into the DI container.
    * Register configuration sections.
    * Register pipeline stages.
    * Subscribe to domain events.
    * Provide alternative repository implementations.

When the plugin system is implemented, register the registry here::

    services.add_singleton(IPluginRegistry, PluginRegistry)
    services.add_singleton(IPluginLoader, FileSystemPluginLoader)

The :class:`~..composition_root.CompositionRoot` exposes an ``extra_modules``
parameter so plugins can register their own services without modifying the
platform's standard modules::

    provider = bootstrap_container(
        config, logging,
        extra_modules=[MyPlugin().as_module()],
    )
"""

from __future__ import annotations

from infrastructure.dependency_injection.interfaces import IServiceCollection


class PluginModule:
    """Registers the plugin registry and extension-point infrastructure.

    **Current status:** placeholder — no registrations yet.

    Future registrations:
        - ``IPluginRegistry`` → ``PluginRegistry`` (singleton)
        - ``IPluginLoader`` → ``FileSystemPluginLoader`` (singleton)

    Extension points exposed to plugins:
        Plugins receive an :class:`~..interfaces.IServiceCollection` slice
        through the ``extra_modules`` mechanism of
        :class:`~..composition_root.CompositionRoot`.  They may register:
        services, repositories, pipeline stages, and event subscribers.
    """

    def register(self, services: IServiceCollection) -> None:  # noqa: ARG002
        """Register plugin infrastructure services.

        Args:
            services: The service collection to register into.
        """
        # No plugin infrastructure yet.
        # Registrations added when the plugin system is introduced.
