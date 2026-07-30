"""Root configuration model — assembles all section configs into one object.

``RootConfig`` is the single object handed to the DI container.
Components receive the specific sub-section they need (e.g.
``Neo4jConfig``) rather than the whole root, keeping dependencies
minimal and making unit tests easy to construct.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from infrastructure.config.models.ai_models import AIModelsConfig
from infrastructure.config.models.application import ApplicationConfig
from infrastructure.config.models.docker import DockerConfig
from infrastructure.config.models.embeddings import EmbeddingsConfig
from infrastructure.config.models.event_bus import EventBusConfig
from infrastructure.config.models.fastapi import FastAPIConfig
from infrastructure.config.models.feature_flags import FeatureFlagsConfig
from infrastructure.config.models.kafka import KafkaConfig
from infrastructure.config.models.logging import LoggingConfig
from infrastructure.config.models.monitoring import MonitoringConfig
from infrastructure.config.models.neo4j import Neo4jConfig
from infrastructure.config.models.pipeline import ProcessingEngineConfig
from infrastructure.config.models.plugins import PluginConfig
from infrastructure.config.models.security import SecurityConfig
from infrastructure.config.models.storage import StorageConfig
from infrastructure.config.models.testing import TestingConfig
from infrastructure.config.models.vector_store import VectorStoreConfig


class RootConfig(BaseModel):
    """Fully resolved, immutable configuration for the RKGB platform.

    This is the single source of truth for all runtime configuration.
    It is built once by :class:`~infrastructure.config.manager.ConfigManager`
    during application bootstrap and then registered with the DI container.

    Each field corresponds to one logical configuration domain.  No field
    should be accessed with ``root_config.neo4j.uri`` in production code —
    inject ``Neo4jConfig`` directly instead.

    Example (DI registration, implemented in the next step)::

        container.define(Neo4jConfig, lambda: root_config.neo4j)
        container.define(FeatureFlagsConfig, lambda: root_config.feature_flags)
    """

    model_config = ConfigDict(frozen=True)

    application: ApplicationConfig = ApplicationConfig()
    fastapi: FastAPIConfig = FastAPIConfig()
    neo4j: Neo4jConfig = Neo4jConfig()
    storage: StorageConfig = StorageConfig()
    logging: LoggingConfig = LoggingConfig()
    security: SecurityConfig = SecurityConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    event_bus: EventBusConfig = EventBusConfig()
    kafka: KafkaConfig = KafkaConfig()
    processing: ProcessingEngineConfig = ProcessingEngineConfig()
    plugins: PluginConfig = PluginConfig()
    ai_models: AIModelsConfig = AIModelsConfig()
    embeddings: EmbeddingsConfig = EmbeddingsConfig()
    vector_store: VectorStoreConfig = VectorStoreConfig()
    feature_flags: FeatureFlagsConfig = FeatureFlagsConfig()
    testing: TestingConfig = TestingConfig()
    docker: DockerConfig = DockerConfig()
