"""Composition Root — the single place where all concrete types are wired.

The Composition Root is the only module in RKGB permitted to instantiate
infrastructure objects and bind them to their abstractions.  All other layers
(application, domain, presentation) receive their dependencies through
constructor injection; none of them reach into the container directly.

Bootstrap order
---------------
1. **Configuration** — :class:`~.modules.configuration_module.ConfigurationModule`
   registers :class:`~infrastructure.config.manager.ConfigManager` and all
   typed config sections as singletons.
2. **Logging** — :class:`~.modules.logging_module.LoggingModule` registers
   :class:`~infrastructure.logging.manager.LoggingManager` and
   :class:`~infrastructure.logging.factory.LoggerFactory` as singletons.
3. **Repositories** — :class:`~.modules.repository_module.RepositoryModule`
   (placeholder; wired in Step A5+).
4. **Processing Engine** — :class:`~.modules.processing_module.ProcessingModule`
   (placeholder; wired in Step B+).
5. **Application Layer** — :class:`~.modules.application_module.ApplicationModule`
   reserves CQRS bus slots (placeholder; buses implemented in Step A5).
6. **Pipeline** — :class:`~.modules.pipeline_module.PipelineModule`
   (placeholder; wired in Step B+).
7. **Plugins** — :class:`~.modules.plugin_module.PluginModule`
   (placeholder; wired when the plugin system is introduced).
8. **Extra modules** — any caller-supplied modules appended last, enabling
   application-specific or plugin registrations.

Usage::

    from infrastructure.dependency_injection.composition_root import CompositionRoot

    root = CompositionRoot(config_manager, logging_manager)
    provider = root.build()

    factory = provider.resolve(LoggerFactory)
"""

from __future__ import annotations

from infrastructure.config.manager import ConfigManager
from infrastructure.dependency_injection.container import DIContainer
from infrastructure.dependency_injection.service_provider import ServiceProvider
from infrastructure.dependency_injection.validators import validate_registrations
from infrastructure.logging.manager import LoggingManager


class CompositionRoot:
    """Wires all application dependencies into a single root ServiceProvider.

    This is the *only* place in the RKGB platform where concrete
    implementations are created and bound to their interfaces.  No other
    module is permitted to manually instantiate infrastructure components.

    Args:
        config_manager: Fully loaded
            :class:`~infrastructure.config.manager.ConfigManager` (produced by
            :func:`~infrastructure.config.bootstrap.bootstrap_config`).
        logging_manager: Initialised
            :class:`~infrastructure.logging.manager.LoggingManager` (produced by
            :func:`~infrastructure.logging.bootstrap.bootstrap_logging`).
        extra_modules: Optional additional registration modules applied after
            the standard platform modules.  Use for application-specific
            overrides, plugin registrations, or test doubles.
        skip_validation: When ``True``, startup validation is bypassed.
            Intended for unit tests that build partial containers.
    """

    def __init__(
        self,
        config_manager: ConfigManager,
        logging_manager: LoggingManager,
        extra_modules: list[object] | None = None,
        *,
        skip_validation: bool = False,
    ) -> None:
        self._config_manager = config_manager
        self._logging_manager = logging_manager
        self._extra_modules: list[object] = extra_modules or []
        self._skip_validation = skip_validation
        self._container = DIContainer()

    def build(self) -> ServiceProvider:
        """Assemble all registrations and return the root :class:`ServiceProvider`.

        Steps:
            1. Apply all registration modules in dependency order.
            2. Run startup validation (unless disabled).
            3. Build and return the :class:`ServiceProvider`.

        Returns:
            Fully configured :class:`~.service_provider.ServiceProvider`.

        Raises:
            :class:`~.exceptions.StartupValidationError`: If any registration
                is invalid and validation is not skipped.
        """
        self._apply_modules()

        if not self._skip_validation:
            validate_registrations(self._container.collection.registrations)

        return self._container.build()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _apply_modules(self) -> None:
        """Apply all registration modules in dependency order."""
        from infrastructure.dependency_injection.modules.application_module import (
            ApplicationModule,
        )
        from infrastructure.dependency_injection.modules.configuration_module import (
            ConfigurationModule,
        )
        from infrastructure.dependency_injection.modules.logging_module import LoggingModule
        from infrastructure.dependency_injection.modules.pipeline_module import PipelineModule
        from infrastructure.dependency_injection.modules.plugin_module import PluginModule
        from infrastructure.dependency_injection.modules.processing_module import ProcessingModule
        from infrastructure.dependency_injection.modules.repository_module import RepositoryModule

        standard_modules: list[object] = [
            ConfigurationModule(self._config_manager),
            LoggingModule(self._logging_manager),
            RepositoryModule(),
            ProcessingModule(),
            ApplicationModule(),
            PipelineModule(),
            PluginModule(),
        ]

        for module in standard_modules + self._extra_modules:
            self._container.add_module(module)
