"""Tests for the ConfigResolver — priority-based merging."""

from __future__ import annotations

import pytest

from infrastructure.config.providers.yaml_provider import RuntimeOverrideProvider
from infrastructure.config.resolver import ConfigResolver, _deep_merge


@pytest.mark.unit()
class TestDeepMerge:
    """Unit tests for the _deep_merge helper."""

    def test_flat_override(self) -> None:
        base = {"a": 1, "b": 2}
        override = {"b": 99, "c": 3}
        result = _deep_merge(base, override)
        assert result == {"a": 1, "b": 99, "c": 3}

    def test_nested_merge_is_recursive(self) -> None:
        base = {"neo4j": {"uri": "bolt://localhost", "port": 7687}}
        override = {"neo4j": {"uri": "bolt://prod-host"}}
        result = _deep_merge(base, override)
        assert result["neo4j"]["uri"] == "bolt://prod-host"
        assert result["neo4j"]["port"] == 7687  # preserved from base

    def test_scalar_overrides_dict(self) -> None:
        base = {"section": {"key": "value"}}
        override = {"section": "scalar"}
        result = _deep_merge(base, override)
        assert result["section"] == "scalar"

    def test_does_not_mutate_base(self) -> None:
        base = {"a": {"b": 1}}
        _deep_merge(base, {"a": {"b": 2}})
        assert base["a"]["b"] == 1

    def test_does_not_mutate_override(self) -> None:
        override = {"a": {"b": 99}}
        _deep_merge({"a": {"b": 1}}, override)
        assert override["a"]["b"] == 99


@pytest.mark.unit()
class TestConfigResolver:
    """Tests for ConfigResolver."""

    def test_empty_providers_returns_empty(self) -> None:
        resolver = ConfigResolver([])
        assert resolver.resolve() == {}

    def test_single_provider(self) -> None:
        p = RuntimeOverrideProvider({"app": {"debug": True}}, priority=10)
        resolver = ConfigResolver([p])
        assert resolver.resolve() == {"app": {"debug": True}}

    def test_higher_priority_wins(self) -> None:
        low = RuntimeOverrideProvider({"app": {"debug": False}}, priority=10)
        high = RuntimeOverrideProvider({"app": {"debug": True}}, priority=40)
        resolver = ConfigResolver([high, low])  # deliberately unsorted
        result = resolver.resolve()
        assert result["app"]["debug"] is True

    def test_nested_keys_merged(self) -> None:
        base = RuntimeOverrideProvider({"neo4j": {"uri": "bolt://a", "db": "rkgb"}}, priority=10)
        override = RuntimeOverrideProvider({"neo4j": {"uri": "bolt://b"}}, priority=20)
        result = ConfigResolver([base, override]).resolve()
        assert result["neo4j"]["uri"] == "bolt://b"
        assert result["neo4j"]["db"] == "rkgb"  # preserved

    def test_unavailable_provider_is_skipped(self) -> None:
        from infrastructure.config.interfaces import ConfigProvider

        class UnavailableProvider(ConfigProvider):
            @property
            def name(self) -> str:
                return "unavailable"

            @property
            def priority(self) -> int:
                return 30

            def load(self) -> dict[str, object]:
                raise AssertionError("Should not be called")

            def is_available(self) -> bool:
                return False

        p_good = RuntimeOverrideProvider({"x": 1}, priority=10)
        p_bad = UnavailableProvider()
        result = ConfigResolver([p_good, p_bad]).resolve()
        assert result == {"x": 1}

    def test_resolve_with_trace_returns_provider_info(self) -> None:
        p = RuntimeOverrideProvider({"k": "v"}, priority=10)
        resolver = ConfigResolver([p])
        merged, trace = resolver.resolve_with_trace()
        assert merged == {"k": "v"}
        assert len(trace) == 1
        assert trace[0]["provider"] == "runtime_override"
        assert trace[0]["available"] is True
