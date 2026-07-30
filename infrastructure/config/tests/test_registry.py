"""Tests for the ConfigRegistry."""

from __future__ import annotations

import pytest
from pydantic import BaseModel

from infrastructure.config.exceptions import ConfigSectionNotFoundError
from infrastructure.config.registry import ConfigRegistry


class _SampleConfig(BaseModel):
    value: str = "default"
    count: int = 0


@pytest.mark.unit()
class TestConfigRegistry:
    """Tests for ConfigRegistry registration and resolution."""

    def test_register_and_is_registered(self) -> None:
        reg = ConfigRegistry()
        reg.register("sample", _SampleConfig)
        assert reg.is_registered("sample") is True

    def test_not_registered_key(self) -> None:
        reg = ConfigRegistry()
        assert reg.is_registered("unknown") is False

    def test_duplicate_registration_raises(self) -> None:
        reg = ConfigRegistry()
        reg.register("sample", _SampleConfig)
        with pytest.raises(ValueError, match="already registered"):
            reg.register("sample", _SampleConfig)

    def test_overwrite_allowed(self) -> None:
        reg = ConfigRegistry()
        reg.register("sample", _SampleConfig)
        reg.register("sample", _SampleConfig, overwrite=True)
        assert reg.is_registered("sample")

    def test_resolve_all_populates_instances(self) -> None:
        reg = ConfigRegistry()
        reg.register("sample", _SampleConfig)
        reg.resolve_all({"sample": {"value": "hello", "count": 5}})
        result = reg.get("sample", _SampleConfig)
        assert result.value == "hello"
        assert result.count == 5

    def test_resolve_all_uses_defaults_for_missing_keys(self) -> None:
        reg = ConfigRegistry()
        reg.register("sample", _SampleConfig)
        reg.resolve_all({})
        result = reg.get("sample", _SampleConfig)
        assert result.value == "default"

    def test_get_before_resolve_raises(self) -> None:
        reg = ConfigRegistry()
        reg.register("sample", _SampleConfig)
        with pytest.raises(RuntimeError, match="not been resolved"):
            reg.get("sample", _SampleConfig)

    def test_get_unknown_key_raises(self) -> None:
        reg = ConfigRegistry()
        with pytest.raises(ConfigSectionNotFoundError):
            reg.get("unknown", _SampleConfig)

    def test_registered_keys_returns_all(self) -> None:
        reg = ConfigRegistry()
        reg.register("a", _SampleConfig)
        reg.register("b", _SampleConfig)
        assert set(reg.registered_keys()) == {"a", "b"}
