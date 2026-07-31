"""Registration modules for the RKGB Dependency Injection Framework.

Each module encapsulates the service registrations for one platform concern.
Modules are applied by the :class:`~..composition_root.CompositionRoot` in
dependency order so that later modules can depend on services registered by
earlier ones.

Standard module order:
    1. :class:`ConfigurationModule` — ConfigManager + all config sections.
    2. :class:`LoggingModule` — LoggingManager + LoggerFactory.
    3. :class:`RepositoryModule` — domain repository implementations (A5+).
    4. :class:`ProcessingModule` — pipeline engine infrastructure (B+).
    5. :class:`ApplicationModule` — CQRS bus slots (A5+).
    6. :class:`PipelineModule` — pipeline DSL + stage infrastructure (B+).
    7. :class:`PluginModule` — plugin registry + extension points.
"""

from __future__ import annotations

from infrastructure.dependency_injection.modules.application_module import ApplicationModule
from infrastructure.dependency_injection.modules.configuration_module import ConfigurationModule
from infrastructure.dependency_injection.modules.logging_module import LoggingModule
from infrastructure.dependency_injection.modules.pipeline_module import PipelineModule
from infrastructure.dependency_injection.modules.plugin_module import PluginModule
from infrastructure.dependency_injection.modules.processing_module import ProcessingModule
from infrastructure.dependency_injection.modules.repository_module import RepositoryModule

__all__ = [
    "ApplicationModule",
    "ConfigurationModule",
    "LoggingModule",
    "PipelineModule",
    "PluginModule",
    "ProcessingModule",
    "RepositoryModule",
]
