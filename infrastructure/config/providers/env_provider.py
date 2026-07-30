"""Environment variable configuration provider.

Reads RKGB-namespaced environment variables and maps them into a nested
dictionary that mirrors the ``RootConfig`` structure.

Convention:
    ``RKGB__<SECTION>__<KEY>=value``

    Double underscores (``__``) separate levels.  This follows Pydantic
    Settings' recommended delimiter for nested models so that future
    migration to ``pydantic-settings`` requires zero structural changes.

Examples:
    ``RKGB__NEO4J__URI=bolt://neo4j:7687``
    ``RKGB__APPLICATION__DEBUG=true``
    ``RKGB__FEATURE_FLAGS__ENABLE_KAFKA=true``
"""

from __future__ import annotations

import os
from typing import Any

from infrastructure.config.constants import ENV_VAR_PREFIX, PRIORITY_ENV_VARS
from infrastructure.config.exceptions import ConfigProviderError
from infrastructure.config.interfaces import ConfigProvider


def _cast_value(raw: str) -> bool | int | float | str:
    """Attempt to cast a raw env-var string to a Python primitive.

    Conversion order: bool → int → float → str.

    Args:
        raw: The raw string value from the environment.

    Returns:
        Cast value.
    """
    lowered = raw.strip().lower()
    if lowered in ("true", "1", "yes", "on"):
        return True
    if lowered in ("false", "0", "no", "off"):
        return False
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        pass
    return raw


def _set_nested(mapping: dict[str, Any], keys: list[str], value: Any) -> None:  # noqa: ANN401
    """Set a deeply nested value in *mapping* using *keys* as the path.

    Args:
        mapping: The dictionary to mutate.
        keys: List of successive key segments forming the path.
        value: The value to store at the leaf.
    """
    for key in keys[:-1]:
        mapping = mapping.setdefault(key, {})
    mapping[keys[-1]] = value


class EnvProvider(ConfigProvider):
    """Loads configuration from OS environment variables.

    Variables must be prefixed with ``RKGB__`` (configurable via
    *prefix*) and use double underscores as path separators.

    Args:
        prefix: Variable prefix (default ``"RKGB__"``).
        priority: Override the default merge priority.
    """

    def __init__(
        self,
        prefix: str = f"{ENV_VAR_PREFIX}_",
        priority: int = PRIORITY_ENV_VARS,
    ) -> None:
        self._prefix = prefix.upper()
        self._priority = priority

    @property
    def name(self) -> str:  # noqa: D102
        return "env"

    @property
    def priority(self) -> int:  # noqa: D102
        return self._priority

    def load(self) -> dict[str, Any]:
        """Read all matching env vars and return a nested dict.

        Returns:
            Nested configuration dictionary.

        Raises:
            ConfigProviderError: On unexpected failures during loading.
        """
        try:
            result: dict[str, Any] = {}
            for key, raw_value in os.environ.items():
                if not key.upper().startswith(self._prefix):
                    continue
                # Strip prefix, split on __ to get path segments
                path = key[len(self._prefix) :].lower().split("__")
                value = _cast_value(raw_value)
                _set_nested(result, path, value)
            return result
        except Exception as exc:
            raise ConfigProviderError(
                provider=self.name,
                reason=str(exc),
            ) from exc

    def is_available(self) -> bool:  # noqa: D102
        """Always available — the OS environment is always accessible."""
        return True
