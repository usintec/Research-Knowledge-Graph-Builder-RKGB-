"""Tests for ConfigManager."""

from __future__ import annotations

import pytest

from infrastructure.config.bootstrap import build_test_config
from infrastructure.config.environment import Environment
from infrastructure.config.manager import ConfigManager
from infrastructure.config.models import FeatureFlagsConfig, Neo4jConfig
from infrastructure.config.models.root import RootConfig
from infrastructure.config.providers.yaml_provider import RuntimeOverrideProvider


@pytest.mark.unit()
class TestConfigManager:
    """Tests for ConfigManager load and access."""

    def _make_manager(self, overrides: dict[str, object] | None = None) -> ConfigManager:
        providers = [
            RuntimeOverrideProvider(
                overrides={"application": {"env": "testing"}, **(overrides or {})},
                priority=50,
            )
        ]
        return ConfigManager(providers=providers, env=Environment.TESTING)

    def test_load_returns_root_config(self) -> None:
        manager = self._make_manager()
        root = manager.load()
        assert isinstance(root, RootConfig)

    def test_load_is_idempotent(self) -> None:
        manager = self._make_manager()
        root1 = manager.load()
        root2 = manager.load()
        assert root1 is root2

    def test_is_loaded_false_before_load(self) -> None:
        manager = self._make_manager()
        assert manager.is_loaded is False

    def test_is_loaded_true_after_load(self) -> None:
        manager = self._make_manager()
        manager.load()
        assert manager.is_loaded is True

    def test_get_returns_correct_section(self) -> None:
        manager = self._make_manager({"neo4j": {"database": "my_db"}})
        neo4j = manager.get(Neo4jConfig)
        assert isinstance(neo4j, Neo4jConfig)
        assert neo4j.database == "my_db"

    def test_get_feature_flags(self) -> None:
        manager = self._make_manager({"feature_flags": {"enable_kafka": True}})
        flags = manager.get(FeatureFlagsConfig)
        assert flags.enable_kafka is True

    def test_get_unknown_type_raises(self) -> None:
        from pydantic import BaseModel

        class UnknownConfig(BaseModel):
            pass

        manager = self._make_manager()
        manager.load()
        with pytest.raises(KeyError):
            manager.get(UnknownConfig)  # type: ignore[type-var]

    def test_reload_clears_and_reloads(self) -> None:
        manager = self._make_manager()
        root1 = manager.load()
        root2 = manager.reload()
        # Different objects but structurally equal
        assert root1 == root2
        assert root1 is not root2

    def test_env_property(self) -> None:
        manager = self._make_manager()
        assert manager.env == Environment.TESTING


@pytest.mark.unit()
class TestBuildTestConfig:
    """Tests for the build_test_config helper."""

    def test_returns_root_config(self) -> None:
        root = build_test_config()
        assert isinstance(root, RootConfig)

    def test_env_is_testing(self) -> None:
        root = build_test_config()
        assert root.application.env == Environment.TESTING

    def test_overrides_applied(self) -> None:
        root = build_test_config({"neo4j": {"database": "custom_test"}})
        assert root.neo4j.database == "custom_test"

    def test_root_config_is_frozen(self) -> None:
        from pydantic import ValidationError

        root = build_test_config()
        with pytest.raises(ValidationError):
            root.neo4j = Neo4jConfig()  # type: ignore[misc]
