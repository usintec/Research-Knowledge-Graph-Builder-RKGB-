"""Tests for configuration providers."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from infrastructure.config.providers.env_provider import EnvProvider, _cast_value, _set_nested
from infrastructure.config.providers.yaml_provider import RuntimeOverrideProvider, YAMLProvider


@pytest.mark.unit()
class TestCastValue:
    """Unit tests for the _cast_value helper."""

    def test_true_variants(self) -> None:
        for raw in ("true", "True", "TRUE", "1", "yes", "on"):
            assert _cast_value(raw) is True

    def test_false_variants(self) -> None:
        for raw in ("false", "False", "FALSE", "0", "no", "off"):
            assert _cast_value(raw) is False

    def test_integer(self) -> None:
        assert _cast_value("42") == 42

    def test_float(self) -> None:
        assert abs(_cast_value("3.14") - 3.14) < 1e-9  # type: ignore[operator]

    def test_string_passthrough(self) -> None:
        assert _cast_value("bolt://localhost:7687") == "bolt://localhost:7687"


@pytest.mark.unit()
class TestSetNested:
    """Unit tests for the _set_nested helper."""

    def test_single_level(self) -> None:
        d: dict[str, object] = {}
        _set_nested(d, ["key"], "value")
        assert d == {"key": "value"}

    def test_two_levels(self) -> None:
        d: dict[str, object] = {}
        _set_nested(d, ["neo4j", "uri"], "bolt://localhost")
        assert d == {"neo4j": {"uri": "bolt://localhost"}}

    def test_three_levels(self) -> None:
        d: dict[str, object] = {}
        _set_nested(d, ["neo4j", "auth", "password"], "s3cr3t")
        assert d["neo4j"]["auth"]["password"] == "s3cr3t"  # type: ignore[index]  # noqa: S105


@pytest.mark.unit()
class TestEnvProvider:
    """Tests for EnvProvider."""

    def test_name(self) -> None:
        assert EnvProvider().name == "env"

    def test_priority_default(self) -> None:
        assert EnvProvider().priority == 40

    def test_is_always_available(self) -> None:
        assert EnvProvider().is_available() is True

    def test_loads_prefixed_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("RKGB__APPLICATION__DEBUG", "true")
        provider = EnvProvider(prefix="RKGB__")
        data = provider.load()
        assert data["application"]["debug"] is True

    def test_ignores_non_prefixed_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("UNRELATED_VAR", "hello")
        provider = EnvProvider(prefix="RKGB__")
        data = provider.load()
        assert "unrelated_var" not in data

    def test_empty_environment_returns_empty_dict(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Remove all RKGB__ vars
        for key in list(os.environ.keys()):
            if key.startswith("RKGB__"):
                monkeypatch.delenv(key)
        provider = EnvProvider(prefix="RKGB__")
        data = provider.load()
        assert isinstance(data, dict)


@pytest.mark.unit()
class TestYAMLProvider:
    """Tests for YAMLProvider."""

    def test_loads_valid_yaml(self, tmp_path: Path) -> None:
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text("app:\n  debug: true\n", encoding="utf-8")
        provider = YAMLProvider(path=yaml_file)
        data = provider.load()
        assert data == {"app": {"debug": True}}

    def test_missing_optional_file_returns_empty(self, tmp_path: Path) -> None:
        provider = YAMLProvider(path=tmp_path / "nonexistent.yaml", optional=True)
        assert provider.load() == {}

    def test_missing_required_file_raises(self, tmp_path: Path) -> None:
        from infrastructure.config.exceptions import ConfigLoadError

        provider = YAMLProvider(path=tmp_path / "nonexistent.yaml", optional=False)
        with pytest.raises(ConfigLoadError):
            provider.load()

    def test_invalid_yaml_raises(self, tmp_path: Path) -> None:
        from infrastructure.config.exceptions import ConfigLoadError

        bad = tmp_path / "bad.yaml"
        bad.write_text(": invalid: yaml: [unclosed", encoding="utf-8")
        provider = YAMLProvider(path=bad)
        with pytest.raises(ConfigLoadError):
            provider.load()

    def test_empty_yaml_returns_empty_dict(self, tmp_path: Path) -> None:
        empty = tmp_path / "empty.yaml"
        empty.write_text("", encoding="utf-8")
        provider = YAMLProvider(path=empty)
        assert provider.load() == {}

    def test_is_available_true_when_file_exists(self, tmp_path: Path) -> None:
        f = tmp_path / "cfg.yaml"
        f.write_text("key: val\n", encoding="utf-8")
        assert YAMLProvider(path=f).is_available() is True

    def test_is_available_false_when_file_missing(self, tmp_path: Path) -> None:
        assert YAMLProvider(path=tmp_path / "nope.yaml").is_available() is False

    def test_name_includes_filename(self, tmp_path: Path) -> None:
        f = tmp_path / "production.yaml"
        f.touch()
        assert "production.yaml" in YAMLProvider(path=f).name


@pytest.mark.unit()
class TestRuntimeOverrideProvider:
    """Tests for RuntimeOverrideProvider."""

    def test_returns_provided_dict(self) -> None:
        data = {"neo4j": {"database": "test"}}
        provider = RuntimeOverrideProvider(overrides=data)
        assert provider.load() == data

    def test_default_priority_is_highest(self) -> None:
        provider = RuntimeOverrideProvider(overrides={})
        assert provider.priority == 50

    def test_is_always_available(self) -> None:
        assert RuntimeOverrideProvider(overrides={}).is_available() is True
