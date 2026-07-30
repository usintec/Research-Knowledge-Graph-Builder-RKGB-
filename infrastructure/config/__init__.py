"""RKGB Configuration Framework.

Provides a centralized, strongly typed, environment-aware configuration
system following Clean Architecture and Twelve-Factor App principles.

Quick start::

    from infrastructure.config.bootstrap import bootstrap_config
    from infrastructure.config.models import Neo4jConfig, FeatureFlagsConfig

    manager = bootstrap_config()
    neo4j: Neo4jConfig = manager.get(Neo4jConfig)
    flags: FeatureFlagsConfig = manager.get(FeatureFlagsConfig)

Key components:

* :class:`~infrastructure.config.manager.ConfigManager` — central orchestrator.
* :class:`~infrastructure.config.models.root.RootConfig` — fully resolved config.
* :mod:`~infrastructure.config.providers` — pluggable config sources.
* :class:`~infrastructure.config.resolver.ConfigResolver` — priority-based merge.
* :class:`~infrastructure.config.registry.ConfigRegistry` — section registry.
* :func:`~infrastructure.config.bootstrap.bootstrap_config` — startup helper.
"""

from __future__ import annotations

from infrastructure.config.bootstrap import bootstrap_config, build_test_config
from infrastructure.config.environment import Environment
from infrastructure.config.exceptions import (
    ConfigError,
    ConfigLoadError,
    ConfigNotInitialisedError,
    ConfigProviderError,
    ConfigSectionNotFoundError,
    ConfigValidationError,
)
from infrastructure.config.manager import ConfigManager
from infrastructure.config.models.root import RootConfig

__all__ = [
    "ConfigError",
    "ConfigLoadError",
    "ConfigManager",
    "ConfigNotInitialisedError",
    "ConfigProviderError",
    "ConfigSectionNotFoundError",
    "ConfigValidationError",
    "Environment",
    "RootConfig",
    "bootstrap_config",
    "build_test_config",
]
