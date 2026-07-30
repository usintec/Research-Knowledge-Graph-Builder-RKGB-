"""Tests for the bootstrap module."""

from __future__ import annotations

from pathlib import Path

import pytest

from infrastructure.config.bootstrap import bootstrap_config, build_test_config
from infrastructure.config.environment import Environment
from infrastructure.config.manager import ConfigManager
from infrastructure.config.models.root import RootConfig


@pytest.mark.unit()
class TestBootstrapConfig:
    """Tests for bootstrap_config()."""

    def test_returns_config_manager(self, tmp_path: Path) -> None:
        manager = bootstrap_config(config_dir=tmp_path, env=Environment.TESTING)
        assert isinstance(manager, ConfigManager)

    def test_manager_is_loaded(self, tmp_path: Path) -> None:
        manager = bootstrap_config(config_dir=tmp_path, env=Environment.TESTING)
        assert manager.is_loaded is True

    def test_env_override_is_respected(self, tmp_path: Path) -> None:
        manager = bootstrap_config(config_dir=tmp_path, env=Environment.DEVELOPMENT)
        assert manager.env == Environment.DEVELOPMENT

    def test_runtime_overrides_applied(self, tmp_path: Path) -> None:
        manager = bootstrap_config(
            config_dir=tmp_path,
            env=Environment.TESTING,
            overrides={"neo4j": {"database": "override_db"}},
        )
        from infrastructure.config.models import Neo4jConfig

        assert manager.get(Neo4jConfig).database == "override_db"

    def test_yaml_config_loaded_when_present(self, tmp_path: Path) -> None:
        yaml_file = tmp_path / "testing.yaml"
        yaml_file.write_text("neo4j:\n  database: from_yaml\n", encoding="utf-8")
        manager = bootstrap_config(config_dir=tmp_path, env=Environment.TESTING)
        from infrastructure.config.models import Neo4jConfig

        assert manager.get(Neo4jConfig).database == "from_yaml"

    def test_missing_yaml_does_not_raise(self, tmp_path: Path) -> None:
        """Bootstrap should succeed even with no YAML files present."""
        manager = bootstrap_config(config_dir=tmp_path, env=Environment.TESTING)
        assert manager.is_loaded is True


@pytest.mark.unit()
class TestBuildTestConfig:
    """Tests for build_test_config()."""

    def test_no_args_returns_root_config(self) -> None:
        root = build_test_config()
        assert isinstance(root, RootConfig)

    def test_is_immutable(self) -> None:
        from pydantic import ValidationError

        root = build_test_config()
        with pytest.raises(ValidationError):
            root.neo4j = None  # type: ignore[misc]
