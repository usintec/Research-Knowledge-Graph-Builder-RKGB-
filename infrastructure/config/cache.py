"""In-process configuration cache implementations.

Provides a simple in-memory cache for resolved configuration objects so
the resolver does not re-run on every access.  The cache is intentionally
process-local and non-distributed — configuration is immutable after
bootstrap, so no invalidation logic is needed in normal operation.
"""

from __future__ import annotations

from typing import Any

from infrastructure.config.interfaces import ConfigCache


class InMemoryConfigCache(ConfigCache):
    """Thread-safe, in-process configuration cache backed by a plain dict.

    Configuration objects are frozen Pydantic models and therefore safe to
    share across threads without copying.  No locking is required here
    because the cache is populated once during bootstrap and then only read.

    Example::

        cache = InMemoryConfigCache()
        cache.set("root", root_config)
        root = cache.get("root")
    """

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}  # Any: config values are heterogeneous

    def get(self, key: str) -> object | None:  # noqa: D102
        return self._store.get(key)

    def set(self, key: str, value: object) -> None:  # noqa: D102
        self._store[key] = value

    def invalidate(self, key: str) -> None:  # noqa: D102
        self._store.pop(key, None)

    def clear(self) -> None:  # noqa: D102
        self._store.clear()

    def __len__(self) -> int:
        return len(self._store)

    def __contains__(self, key: object) -> bool:
        return key in self._store


class NullConfigCache(ConfigCache):
    """No-op cache — every ``get()`` returns ``None``.

    Useful in testing when you want to force the resolver to run on every
    access, or when you want to confirm that the cache is bypassed.
    """

    def get(self, key: str) -> None:  # noqa: D102
        return None

    def set(self, key: str, value: object) -> None:  # noqa: D102
        pass

    def invalidate(self, key: str) -> None:  # noqa: D102
        pass

    def clear(self) -> None:  # noqa: D102
        pass
