"""Configuration section registry.

The registry maps string keys to typed configuration model classes and
their resolved instances.  It supports:

* Lazy loading — sections are resolved on first access.
* Plugin registration — third-party packages register their own sections.
* Type-safe retrieval — ``get()`` returns the correct Pydantic model.
* Version awareness — each section carries a schema version string.

The registry itself holds no state between application restarts; it is
rebuilt during bootstrap.
"""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel

from infrastructure.config.exceptions import ConfigSectionNotFoundError

ModelT = TypeVar("ModelT", bound=BaseModel)


class _SectionEntry:
    """Internal record for a registered configuration section."""

    __slots__ = ("key", "model_type", "instance", "version", "description")

    def __init__(
        self,
        key: str,
        model_type: type[BaseModel],
        version: str = "1.0",
        description: str = "",
    ) -> None:
        self.key = key
        self.model_type = model_type
        self.instance: BaseModel | None = None
        self.version = version
        self.description = description


class ConfigRegistry:
    """Registry of configuration sections.

    Usage::

        registry = ConfigRegistry()
        registry.register("neo4j", Neo4jConfig)
        registry.resolve_all(merged_dict)

        neo4j_cfg = registry.get("neo4j", Neo4jConfig)

    Plugins register additional sections::

        registry.register(
            "my_plugin",
            MyPluginConfig,
            version="1.0",
            description="My plugin configuration",
        )
    """

    def __init__(self) -> None:
        self._sections: dict[str, _SectionEntry] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        key: str,
        model_type: type[BaseModel],
        *,
        version: str = "1.0",
        description: str = "",
        overwrite: bool = False,
    ) -> None:
        """Register a configuration section.

        Args:
            key: Unique string identifier (e.g. ``"neo4j"``).
            model_type: Pydantic model class for this section.
            version: Schema version string for this section.
            description: Human-readable description.
            overwrite: If ``True``, replace an existing registration.

        Raises:
            ValueError: If *key* is already registered and *overwrite* is ``False``.
        """
        if key in self._sections and not overwrite:
            raise ValueError(
                f"Configuration section '{key}' is already registered. "
                "Use overwrite=True to replace it."
            )
        self._sections[key] = _SectionEntry(
            key=key,
            model_type=model_type,
            version=version,
            description=description,
        )

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    def resolve_all(self, merged: dict[str, Any]) -> None:
        """Instantiate all registered sections from the merged config dict.

        Args:
            merged: Fully merged raw configuration dictionary from the resolver.
        """
        for key, entry in self._sections.items():
            section_data = merged.get(key, {})
            entry.instance = entry.model_type.model_validate(section_data)

    def resolve_section(self, key: str, data: dict[str, Any]) -> BaseModel:
        """Resolve a single section (useful for lazy / hot-reload).

        Args:
            key: Section key.
            data: Raw data dict for this section.

        Returns:
            Validated model instance.

        Raises:
            ConfigSectionNotFoundError: If *key* is not registered.
        """
        entry = self._get_entry(key)
        entry.instance = entry.model_type.model_validate(data)
        return entry.instance

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get(self, key: str, model_type: type[ModelT]) -> ModelT:
        """Retrieve a resolved configuration section by key.

        Args:
            key: Section key.
            model_type: Expected model type (used for type narrowing).

        Returns:
            Resolved model instance.

        Raises:
            ConfigSectionNotFoundError: If *key* is not registered.
            RuntimeError: If the section has not been resolved yet.
        """
        entry = self._get_entry(key)
        if entry.instance is None:
            raise RuntimeError(
                f"Configuration section '{key}' has not been resolved. "
                "Call resolve_all() before accessing sections."
            )
        return entry.instance  # type: ignore[return-value]

    def is_registered(self, key: str) -> bool:
        """Return ``True`` if *key* is registered.

        Args:
            key: Section key.

        Returns:
            ``True`` if registered.
        """
        return key in self._sections

    def registered_keys(self) -> list[str]:
        """Return all registered section keys.

        Returns:
            List of key strings.
        """
        return list(self._sections.keys())

    def _get_entry(self, key: str) -> _SectionEntry:
        if key not in self._sections:
            raise ConfigSectionNotFoundError(key)
        return self._sections[key]
