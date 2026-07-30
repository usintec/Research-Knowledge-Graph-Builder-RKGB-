"""Feature flag configuration model.

Feature flags control which platform capabilities are active at runtime.
They allow new features to be deployed but kept dormant until explicitly
enabled, supporting trunk-based development and progressive roll-out.

All flags default to ``False`` — opt-in rather than opt-out.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class FeatureFlagsConfig(BaseModel):
    """Platform-wide feature flag registry.

    Flags are injectable via the DI container so components receive a
    typed ``FeatureFlagsConfig`` rather than reading env vars directly.

    Adding a new flag:
        1. Add a field here with a ``False`` default.
        2. Document its purpose in the field docstring.
        3. Set it to ``True`` in the appropriate environment YAML.
    """

    model_config = ConfigDict(frozen=True)

    # Core capabilities
    enable_graph_rag: bool = False
    """Enable the GraphRAG pipeline and query engine."""

    enable_kafka: bool = False
    """Use Kafka as the event bus instead of the in-process bus."""

    enable_plugin_loader: bool = False
    """Activate the dynamic plugin discovery and loading system."""

    enable_experimental_pipelines: bool = False
    """Allow experimental pipeline stages to be registered and executed."""

    # Observability
    enable_metrics: bool = False
    """Expose Prometheus metrics at ``/metrics``."""

    enable_tracing: bool = False
    """Enable OpenTelemetry distributed tracing."""

    enable_profiling: bool = False
    """Enable async profiling (development/staging only)."""

    # Infrastructure
    enable_hot_reload: bool = False
    """Allow configuration hot-reload without restarting the server."""

    enable_cache: bool = True
    """Enable the application-level Redis cache."""

    enable_vector_store: bool = False
    """Enable vector database integration for semantic search."""

    # AI
    enable_llm_extraction: bool = False
    """Enable LLM-powered knowledge extraction in the processing pipeline."""

    enable_embeddings: bool = False
    """Enable embedding generation for documents and entities."""

    def is_enabled(self, flag_name: str) -> bool:
        """Check a feature flag by name at runtime.

        Args:
            flag_name: The attribute name of the flag (e.g. ``"enable_kafka"``).

        Returns:
            ``True`` if the flag exists and is enabled.

        Raises:
            AttributeError: If the flag name does not exist.
        """
        value = getattr(self, flag_name)
        if not isinstance(value, bool):
            raise TypeError(f"Flag '{flag_name}' is not a boolean field.")
        return value
