"""Configuration resolver — merges providers and applies precedence.

The resolver collects raw dictionaries from all registered providers
(sorted by ascending priority), deep-merges them so that higher-priority
values win on conflict, and returns the final merged dictionary ready
for Pydantic model instantiation.
"""

from __future__ import annotations

from typing import Any

from infrastructure.config.interfaces import ConfigProvider


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge *override* into *base* (non-destructive).

    Nested dicts are merged recursively; scalar values in *override*
    replace those in *base*.  Neither input is mutated.

    Args:
        base: Lower-priority mapping.
        override: Higher-priority mapping.

    Returns:
        New merged dictionary.
    """
    merged = dict(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


class ConfigResolver:
    """Merges configuration from multiple providers respecting priority.

    Usage::

        resolver = ConfigResolver(providers=[yaml_provider, env_provider])
        merged = resolver.resolve()

    Args:
        providers: List of :class:`~infrastructure.config.interfaces.ConfigProvider`
            instances.  May be unsorted — the resolver sorts by priority
            internally.
    """

    def __init__(self, providers: list[ConfigProvider]) -> None:
        self._providers = sorted(providers, key=lambda p: p.priority)

    @property
    def providers(self) -> list[ConfigProvider]:
        """Providers sorted by ascending priority.

        Returns:
            Ordered list of providers.
        """
        return list(self._providers)

    def resolve(self) -> dict[str, Any]:
        """Load all providers and produce a single merged dictionary.

        Providers are applied in ascending priority order so that the
        last write wins on conflicts.

        Returns:
            Fully merged raw configuration dictionary.
        """
        merged: dict[str, Any] = {}
        for provider in self._providers:
            if not provider.is_available():
                continue
            data = provider.load()
            merged = _deep_merge(merged, data)
        return merged

    def resolve_with_trace(self) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Resolve config and return a trace of each provider's contribution.

        Useful for debugging configuration precedence.

        Returns:
            Tuple of ``(merged_dict, trace)`` where *trace* is a list of
            ``{"provider": name, "priority": int, "available": bool, "data": dict}``
            dicts, one per provider.
        """
        merged: dict[str, Any] = {}
        trace: list[dict[str, Any]] = []
        for provider in self._providers:
            available = provider.is_available()
            data = provider.load() if available else {}
            trace.append(
                {
                    "provider": provider.name,
                    "priority": provider.priority,
                    "available": available,
                    "data": data,
                }
            )
            if available:
                merged = _deep_merge(merged, data)
        return merged, trace
