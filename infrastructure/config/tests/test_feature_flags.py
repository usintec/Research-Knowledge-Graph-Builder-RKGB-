"""Tests for FeatureFlagsConfig."""

from __future__ import annotations

import pytest

from infrastructure.config.bootstrap import build_test_config
from infrastructure.config.models.feature_flags import FeatureFlagsConfig


@pytest.mark.unit()
class TestFeatureFlagsConfig:
    """Tests for feature flag behaviour."""

    def test_all_flags_default_false_except_cache(self) -> None:
        flags = FeatureFlagsConfig()
        assert flags.enable_graph_rag is False
        assert flags.enable_kafka is False
        assert flags.enable_plugin_loader is False
        assert flags.enable_experimental_pipelines is False
        assert flags.enable_metrics is False
        assert flags.enable_tracing is False
        assert flags.enable_vector_store is False
        assert flags.enable_llm_extraction is False

    def test_cache_enabled_by_default(self) -> None:
        assert FeatureFlagsConfig().enable_cache is True

    def test_is_enabled_returns_true(self) -> None:
        flags = FeatureFlagsConfig(enable_kafka=True)
        assert flags.is_enabled("enable_kafka") is True

    def test_is_enabled_returns_false(self) -> None:
        flags = FeatureFlagsConfig()
        assert flags.is_enabled("enable_kafka") is False

    def test_is_enabled_invalid_name_raises(self) -> None:
        flags = FeatureFlagsConfig()
        with pytest.raises(AttributeError):
            flags.is_enabled("nonexistent_flag")

    def test_flags_are_immutable(self) -> None:
        from pydantic import ValidationError

        flags = FeatureFlagsConfig()
        with pytest.raises(ValidationError):
            flags.enable_kafka = True  # type: ignore[misc]

    def test_overrides_via_build_test_config(self) -> None:
        root = build_test_config({"feature_flags": {"enable_graph_rag": True}})
        assert root.feature_flags.enable_graph_rag is True
