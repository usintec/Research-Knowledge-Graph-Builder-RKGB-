"""Configuration Manager — the central orchestrator.

``ConfigManager`` is the single authority for all configuration in RKGB.
It loads providers, merges them via the resolver, validates the result,
caches the resolved root, and exposes typed section access.

**Only one instance should exist per application process.**  The DI
container (implemented in the next step) is responsible for enforcing
this by binding ``ConfigManager`` as a singleton.

Integration with the DI container (preview)::

    # In the composition root (infrastructure/dependency_injection/):
    container.define(ConfigManager, lambda: manager)
    container.define(Neo4jConfig, lambda: manager.get(Neo4jConfig))
    container.define(FeatureFlagsConfig, lambda: manager.get(FeatureFlagsConfig))
"""

from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel, ValidationError

from infrastructure.config.cache import InMemoryConfigCache
from infrastructure.config.environment import Environment
from infrastructure.config.exceptions import ConfigValidationError
from infrastructure.config.interfaces import ConfigCache, ConfigProvider
from infrastructure.config.models.root import RootConfig
from infrastructure.config.registry import ConfigRegistry
from infrastructure.config.resolver import ConfigResolver
from infrastructure.config.validators import ValidationRegistry, default_registry

ModelT = TypeVar("ModelT", bound=BaseModel)

def _find_root_attr(root: RootConfig, model_type: type[BaseModel]) -> BaseModel | None:
    """Locate the field on *root* whose value is an instance of *model_type*.

    Args:
        root: The fully resolved root configuration.
        model_type: The Pydantic model class to look up.

    Returns:
        The matching section instance, or ``None`` if not found.
    """
    for field_name in type(root).model_fields:
        value = getattr(root, field_name)
        if isinstance(value, model_type):
            return value
    return None


class ConfigManager:
    """Central configuration manager for RKGB.

    Args:
        providers: Ordered list of configuration providers.
        cache: Cache implementation (defaults to ``InMemoryConfigCache``).
        registry: Section registry (defaults to a fresh ``ConfigRegistry``
            pre-populated with all core sections).
        validation_registry: Cross-field validator registry.
        env: Active environment (auto-detected from ``APP_ENV`` if ``None``).
    """

    def __init__(
        self,
        providers: list[ConfigProvider],
        cache: ConfigCache | None = None,
        registry: ConfigRegistry | None = None,
        validation_registry: ValidationRegistry | None = None,
        env: Environment | None = None,
    ) -> None:
        self._resolver = ConfigResolver(providers)
        self._cache: ConfigCache = cache or InMemoryConfigCache()
        self._registry = registry or _build_default_registry()
        self._validation_registry = validation_registry or default_registry
        self._env = env or Environment.current()
        self._root: RootConfig | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def load(self) -> RootConfig:
        """Load, merge, validate, and cache the full configuration.

        This method is idempotent — calling it multiple times returns the
        same cached object.

        Returns:
            Fully resolved :class:`~infrastructure.config.models.root.RootConfig`.

        Raises:
            ConfigValidationError: If Pydantic validation or cross-field
                validation fails.
        """
        if self._root is not None:
            return self._root

        merged = self._resolver.resolve()

        try:
            root = RootConfig.model_validate(merged)
        except ValidationError as exc:
            raise ConfigValidationError(
                section="root",
                details=str(exc),
            ) from exc

        self._validation_registry.validate_all(root, self._env)
        self._root = root
        self._cache.set("root", root)
        return root

    def reload(self) -> RootConfig:
        """Force a fresh load, bypassing the cache.

        Returns:
            Freshly resolved :class:`~infrastructure.config.models.root.RootConfig`.
        """
        self._root = None
        self._cache.clear()
        return self.load()

    # ------------------------------------------------------------------
    # Access
    # ------------------------------------------------------------------

    @property
    def root(self) -> RootConfig:
        """Return the resolved root config, loading it if necessary.

        Returns:
            :class:`~infrastructure.config.models.root.RootConfig`.
        """
        return self.load()

    def get(self, model_type: type[ModelT]) -> ModelT:
        """Retrieve a typed configuration section by model class.

        Args:
            model_type: The Pydantic model class of the desired section.

        Returns:
            Resolved, frozen configuration model instance.

        Raises:
            ConfigNotInitialisedError: If ``load()`` has not been called.
            KeyError: If *model_type* is not a known root section.

        Example::

            neo4j_cfg: Neo4jConfig = manager.get(Neo4jConfig)
        """
        root = self.root
        section = _find_root_attr(root, model_type)
        if section is None:
            raise KeyError(
                f"{model_type.__name__} is not a registered root config section."
            )
        return section  # type: ignore[return-value]

    @property
    def env(self) -> Environment:
        """Active deployment environment.

        Returns:
            :class:`~infrastructure.config.environment.Environment`.
        """
        return self._env

    @property
    def is_loaded(self) -> bool:
        """Return ``True`` if configuration has been loaded.

        Returns:
            ``bool``.
        """
        return self._root is not None


def _build_default_registry() -> ConfigRegistry:
    """Construct a :class:`ConfigRegistry` pre-populated with all core sections.

    Returns:
        Populated :class:`ConfigRegistry`.
    """
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

    reg = ConfigRegistry()
    sections: list[tuple[str, type[BaseModel], str]] = [
        ("application", ApplicationConfig, "Core application settings"),
        ("fastapi", FastAPIConfig, "FastAPI framework settings"),
        ("neo4j", Neo4jConfig, "Neo4j graph database connection"),
        ("storage", StorageConfig, "File and object storage"),
        ("logging", LoggingConfig, "Logging and observability"),
        ("security", SecurityConfig, "Authentication and security"),
        ("monitoring", MonitoringConfig, "Metrics, tracing, health"),
        ("event_bus", EventBusConfig, "Internal event bus"),
        ("kafka", KafkaConfig, "Apache Kafka integration"),
        ("processing", ProcessingEngineConfig, "Pipeline engine"),
        ("plugins", PluginConfig, "Plugin system"),
        ("ai_models", AIModelsConfig, "AI model providers"),
        ("embeddings", EmbeddingsConfig, "Embedding generation"),
        ("vector_store", VectorStoreConfig, "Vector database"),
        ("feature_flags", FeatureFlagsConfig, "Feature flags"),
        ("testing", TestingConfig, "Test environment settings"),
        ("docker", DockerConfig, "Docker deployment"),
    ]
    for key, model, desc in sections:
        reg.register(key, model, description=desc)
    return reg
