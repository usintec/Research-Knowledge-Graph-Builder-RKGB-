"""YAML file configuration provider.

Loads configuration from a YAML file on disk.  Used for both the base
config (``configs/base.yaml``) and environment-specific overrides
(e.g. ``configs/production.yaml``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from infrastructure.config.constants import PRIORITY_BASE_YAML
from infrastructure.config.exceptions import ConfigLoadError, ConfigProviderError
from infrastructure.config.interfaces import ConfigProvider


class YAMLProvider(ConfigProvider):
    """Loads configuration from a YAML file.

    Args:
        path: Absolute or relative path to the YAML file.
        priority: Merge priority.  Use :data:`~infrastructure.config.constants.PRIORITY_BASE_YAML`
            for base config and :data:`~infrastructure.config.constants.PRIORITY_ENV_YAML`
            for environment-specific overrides.
        optional: If ``True``, a missing file yields an empty dict rather
            than raising an exception.

    Example::

        provider = YAMLProvider(
            path=Path("configs/development.yaml"),
            priority=PRIORITY_ENV_YAML,
        )
        data = provider.load()
    """

    def __init__(
        self,
        path: Path | str,
        priority: int = PRIORITY_BASE_YAML,
        *,
        optional: bool = False,
    ) -> None:
        self._path = Path(path)
        self._priority = priority
        self._optional = optional

    @property
    def name(self) -> str:  # noqa: D102
        return f"yaml:{self._path.name}"

    @property
    def priority(self) -> int:  # noqa: D102
        return self._priority

    @property
    def path(self) -> Path:
        """Resolved file path for this provider.

        Returns:
            ``Path`` instance.
        """
        return self._path

    def is_available(self) -> bool:  # noqa: D102
        """Return ``True`` if the YAML file exists and is readable."""
        return self._path.is_file()

    def load(self) -> dict[str, Any]:
        """Parse the YAML file and return its contents as a dict.

        Returns:
            Parsed YAML as a nested dictionary, or ``{}`` if the file is
            missing and *optional* is ``True``.

        Raises:
            ConfigLoadError: If the file is missing (non-optional) or invalid.
            ConfigProviderError: On unexpected I/O errors.
        """
        if not self._path.is_file():
            if self._optional:
                return {}
            raise ConfigLoadError(
                source=str(self._path),
                reason="File not found.",
            )

        try:
            raw = self._path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ConfigProviderError(
                provider=self.name,
                reason=f"I/O error reading file: {exc}",
            ) from exc

        try:
            data = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            raise ConfigLoadError(
                source=str(self._path),
                reason=f"Invalid YAML: {exc}",
            ) from exc

        if data is None:
            return {}

        if not isinstance(data, dict):
            raise ConfigLoadError(
                source=str(self._path),
                reason=f"Expected a YAML mapping at the root, got {type(data).__name__}.",
            )

        return data  # type: ignore[return-value]


class RuntimeOverrideProvider(ConfigProvider):
    """In-memory provider for programmatic / test-time overrides.

    Accepts a pre-built dictionary and returns it verbatim.  Useful in
    unit tests where you want to override a single value without touching
    files or the real environment.

    Args:
        overrides: Nested dict of configuration overrides.
        priority: Merge priority (defaults to 50 — highest).

    Example::

        provider = RuntimeOverrideProvider(
            overrides={"neo4j": {"database": "test_db"}},
        )
    """

    def __init__(
        self,
        overrides: dict[str, Any],
        priority: int = 50,
    ) -> None:
        self._overrides = overrides
        self._priority = priority

    @property
    def name(self) -> str:  # noqa: D102
        return "runtime_override"

    @property
    def priority(self) -> int:  # noqa: D102
        return self._priority

    def load(self) -> dict[str, Any]:  # noqa: D102
        return dict(self._overrides)
