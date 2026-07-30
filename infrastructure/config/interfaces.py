"""Abstract interfaces for the RKGB Configuration Framework.

All configuration components depend on these interfaces, not concrete
implementations — following the Dependency Inversion Principle.

Design note: ABCs are used over Protocols here because configuration
providers carry state (priority, name) and benefit from enforcement of
method signatures at class-definition time rather than at call sites.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class ConfigProvider(ABC):
    """Abstract base for every configuration provider.

    A provider loads raw configuration data from exactly one source
    (env vars, YAML file, secrets manager, etc.) and returns it as a
    plain dictionary.  Providers are stateless with respect to content —
    they produce a fresh snapshot on each ``load()`` call.

    Priority determines merge order: higher priority overrides lower.

    Example::

        class MyProvider(ConfigProvider):
            @property
            def name(self) -> str:
                return "my_provider"

            @property
            def priority(self) -> int:
                return 50

            def load(self) -> dict[str, Any]:
                return {"app": {"debug": True}}
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable identifier for this provider.

        Returns:
            Provider name (e.g. ``"yaml"``, ``"env"``).
        """

    @property
    @abstractmethod
    def priority(self) -> int:
        """Merge priority — higher value wins on conflict.

        Standard scale (mirrors Twelve-Factor App hierarchy):
            10  — Default values
            20  — Base YAML
            30  — Environment-specific YAML
            40  — Environment variables
            50  — Runtime overrides

        Returns:
            Integer priority value.
        """

    @abstractmethod
    def load(self) -> dict[str, Any]:  # noqa: ANN401
        """Load and return raw configuration as a nested dictionary.

        Returns:
            Nested dict of configuration values.

        Raises:
            ConfigProviderError: If the source is unavailable or malformed.
        """

    def is_available(self) -> bool:
        """Return ``True`` if this provider's source is reachable.

        Subclasses should override to perform lightweight availability
        checks (e.g. file existence, env var presence) without loading.

        Returns:
            ``True`` by default — providers are assumed available.
        """
        return True


class ConfigCache(ABC):
    """Abstract cache for resolved configuration objects."""

    @abstractmethod
    def get(self, key: str) -> object | None:
        """Retrieve a cached value.

        Args:
            key: Cache key.

        Returns:
            Cached value or ``None`` if absent.
        """

    @abstractmethod
    def set(self, key: str, value: object) -> None:
        """Store a value in the cache.

        Args:
            key: Cache key.
            value: Value to cache.
        """

    @abstractmethod
    def invalidate(self, key: str) -> None:
        """Remove a single entry from the cache.

        Args:
            key: Cache key to invalidate.
        """

    @abstractmethod
    def clear(self) -> None:
        """Remove all entries from the cache."""


class ConfigValidator(ABC):
    """Abstract validator for configuration model instances."""

    @abstractmethod
    def validate(self, config: BaseModel) -> None:
        """Validate a configuration model.

        Args:
            config: Pydantic model instance to validate.

        Raises:
            ConfigValidationError: If validation fails.
        """


class ConfigLoader(ABC):
    """Abstract loader for reading raw configuration from a file or URL."""

    @abstractmethod
    def load(self, source: str) -> dict[str, Any]:  # noqa: ANN401
        """Load configuration from the given source path or URL.

        Args:
            source: File path or URL string.

        Returns:
            Parsed configuration dictionary.

        Raises:
            ConfigLoadError: If the source cannot be read or parsed.
        """
