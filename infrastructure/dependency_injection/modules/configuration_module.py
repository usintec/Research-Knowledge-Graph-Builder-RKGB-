"""Configuration registration module.

Registers :class:`~infrastructure.config.manager.ConfigManager` and every
typed configuration section as application-lifetime singletons.

All sections are lazily resolved from the :class:`ConfigManager` on first
access, which ensures they are always consistent with the loaded config.

This module is always the first to be applied by the
:class:`~..composition_root.CompositionRoot`.
"""

from __future__ import annotations

from infrastructure.config.manager import ConfigManager
from infrastructure.config.models import (
    AIModelsConfig,
    ApplicationConfig,
    DockerConfig,
    EmbeddingsConfig,
    EventBusConfig,
    FastAPIConfig,
    FeatureFlagsConfig,
    KafkaConfig,
    LoggingConfig,
    MonitoringConfig,
    Neo4jConfig,
    PluginConfig,
    ProcessingEngineConfig,
    SecurityConfig,
    StorageConfig,
    TestingConfig,
    VectorStoreConfig,
)
from infrastructure.dependency_injection.interfaces import IServiceCollection


class ConfigurationModule:
    """Registers ConfigManager and all typed config sections as singletons.

    Args:
        config_manager: The fully loaded
            :class:`~infrastructure.config.manager.ConfigManager` produced
            during startup by
            :func:`~infrastructure.config.bootstrap.bootstrap_config`.
    """

    def __init__(self, config_manager: ConfigManager) -> None:
        self._config_manager = config_manager

    def register(self, services: IServiceCollection) -> None:
        """Register all configuration services.

        Registered services:
            - :class:`~infrastructure.config.manager.ConfigManager` (singleton, pre-built)
            - All typed config section classes (singleton, resolved via factory)

        Args:
            services: The :class:`~..service_collection.ServiceCollection` to
                register into.
        """
        manager = self._config_manager

        # The manager itself is pre-built — register as instance singleton.
        services.add_singleton(ConfigManager, instance=manager)

        # Each typed config section is a singleton resolved lazily from the manager.
        # The factory captures `st` by value to avoid the loop-variable closure pitfall.
        _section_types: list[type] = [
            ApplicationConfig,
            FastAPIConfig,
            Neo4jConfig,
            StorageConfig,
            LoggingConfig,
            SecurityConfig,
            MonitoringConfig,
            EventBusConfig,
            KafkaConfig,
            ProcessingEngineConfig,
            PluginConfig,
            AIModelsConfig,
            EmbeddingsConfig,
            VectorStoreConfig,
            FeatureFlagsConfig,
            TestingConfig,
            DockerConfig,
        ]

        for section_type in _section_types:
            _st = section_type  # explicit capture for the factory closure
            services.add_singleton(
                _st,
                factory=lambda p, st=_st: p.resolve(ConfigManager).get(st),
            )
