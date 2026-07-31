"""ServiceProvider — runtime dependency resolution and lifetime management.

The provider is the *resolution* phase of the DI lifecycle.  It receives a
snapshot of :class:`~.registration.ServiceRegistration` objects from the
:class:`~.service_collection.ServiceCollection` and constructs service
instances on demand, managing singleton caches, scope isolation, circular
dependency detection, and constructor injection.

Hierarchy::

    ServiceProvider  (root — owns singleton cache)
        └─ ServiceScope
               └─ ServiceProvider  (scope — shares singleton cache, owns scoped cache)
"""

from __future__ import annotations

import inspect
import typing
from typing import Any

from infrastructure.dependency_injection.exceptions import (
    CircularDependencyError,
    ScopeError,
    ServiceNotFoundError,
    ServiceResolutionError,
)
from infrastructure.dependency_injection.lifetimes import ServiceLifetime
from infrastructure.dependency_injection.registration import ServiceRegistration


class ServiceScope:
    """An isolated execution scope for scoped service resolution.

    Scoped services created inside this scope share a single instance
    within the scope boundary and are discarded on exit.  Singleton
    services are still shared with the parent provider.

    Usage::

        with provider.create_scope() as scoped_provider:
            ctx = scoped_provider.resolve(PipelineContext)
            # ctx is cached for the duration of this block only
        # scoped cache cleared here

        # or without context manager:
        scope = provider.create_scope()
        scoped_provider = scope.provider
        ...
        scope.__exit__(None, None, None)  # manual disposal

    Args:
        parent_provider: The root (or parent) :class:`ServiceProvider` from
            which to inherit the singleton cache and registrations.
    """

    def __init__(self, parent_provider: "ServiceProvider") -> None:
        self._scoped_instances: dict[type, Any] = {}
        self._provider = ServiceProvider(
            parent_provider._registrations,
            _singletons=parent_provider._singletons,
            _scoped_instances=self._scoped_instances,
            _in_scope=True,
        )

    def __enter__(self) -> "ServiceProvider":
        """Enter the scope and return the scoped provider."""
        return self._provider

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the scope, clearing all scoped instance caches."""
        self._scoped_instances.clear()

    @property
    def provider(self) -> "ServiceProvider":
        """Return the scoped :class:`ServiceProvider`."""
        return self._provider


class ServiceProvider:
    """Resolves services by type, constructing and managing their lifetimes.

    You do not normally instantiate this directly — obtain one from
    :meth:`~.service_collection.ServiceCollection.build_provider` or via the
    :class:`~.container.DIContainer`.

    Resolution precedence for each registration:
        1. Pre-built ``instance`` — returned as-is (only valid for singletons).
        2. ``factory`` — called with this provider as its sole argument.
        3. Constructor injection — ``__init__`` parameters resolved recursively.

    Lifetime behaviour:
        * ``SINGLETON``: Instance stored in ``_singletons``; shared across
          all scopes for the application lifetime.
        * ``SCOPED``: Instance stored in ``_scoped_instances``; isolated
          to one scope.  Raises :class:`~.exceptions.ScopeError` if resolved
          outside a scope.
        * ``TRANSIENT``: Fresh instance on every call; no caching.

    Args:
        registrations: Map of service type → :class:`~.registration.ServiceRegistration`.
        _singletons: Shared singleton cache (injected by :class:`ServiceScope`
            so child scopes share the same singleton instances).
        _scoped_instances: Per-scope instance cache (injected by :class:`ServiceScope`).
        _in_scope: ``True`` when this provider is owned by a :class:`ServiceScope`.
    """

    def __init__(
        self,
        registrations: dict[type, ServiceRegistration],
        *,
        _singletons: dict[type, Any] | None = None,
        _scoped_instances: dict[type, Any] | None = None,
        _in_scope: bool = False,
    ) -> None:
        self._registrations = registrations
        self._singletons: dict[type, Any] = _singletons if _singletons is not None else {}
        self._scoped_instances: dict[type, Any] | None = _scoped_instances
        self._in_scope = _in_scope
        self._resolving: set[type] = set()

    # ------------------------------------------------------------------
    # Public resolution API
    # ------------------------------------------------------------------

    def resolve(self, service_type: type) -> Any:
        """Resolve the given service type.

        Args:
            service_type: The abstract or concrete type to resolve.

        Returns:
            A fully constructed instance with all dependencies injected.

        Raises:
            ServiceNotFoundError: If *service_type* is not registered.
            CircularDependencyError: If a circular dependency is detected.
            ServiceResolutionError: If construction fails for any other reason.
            ScopeError: If a scoped service is resolved outside of a scope.
        """
        if service_type not in self._registrations:
            raise ServiceNotFoundError(service_type)

        reg = self._registrations[service_type]

        if reg.lifetime is ServiceLifetime.SINGLETON:
            if service_type not in self._singletons:
                self._singletons[service_type] = self._build(reg)
            return self._singletons[service_type]

        if reg.lifetime is ServiceLifetime.SCOPED:
            if not self._in_scope or self._scoped_instances is None:
                raise ScopeError(
                    f"Cannot resolve scoped service '{service_type.__qualname__}' "
                    "outside of an active scope. Use provider.create_scope() first."
                )
            if service_type not in self._scoped_instances:
                self._scoped_instances[service_type] = self._build(reg)
            return self._scoped_instances[service_type]

        # TRANSIENT — always build a fresh instance.
        return self._build(reg)

    def try_resolve(self, service_type: type) -> Any | None:
        """Resolve *service_type*, returning ``None`` if not registered.

        All other resolution errors (e.g. :class:`~.exceptions.CircularDependencyError`)
        are still propagated.

        Args:
            service_type: The type to resolve.

        Returns:
            Resolved instance, or ``None`` when not registered.
        """
        try:
            return self.resolve(service_type)
        except ServiceNotFoundError:
            return None

    def create_scope(self) -> ServiceScope:
        """Create a child :class:`ServiceScope` for scoped service resolution.

        The scope shares the singleton cache with this provider but maintains
        its own isolated scoped instance cache.

        Returns:
            A new :class:`ServiceScope` ready for use as a context manager.
        """
        return ServiceScope(self)

    # ------------------------------------------------------------------
    # Internal construction
    # ------------------------------------------------------------------

    def _build(self, reg: ServiceRegistration) -> Any:
        """Construct a service instance from its :class:`~.registration.ServiceRegistration`.

        Guards against circular dependencies by tracking the types currently
        in the resolution chain.

        Args:
            reg: The registration describing how to build the service.

        Returns:
            Constructed service instance.

        Raises:
            CircularDependencyError: If *reg.service_type* appears in the
                active resolution chain.
            ServiceResolutionError: If construction raises any other exception.
        """
        service_type = reg.service_type

        if service_type in self._resolving:
            # Materialise the cycle as a readable chain for the error message.
            chain = list(self._resolving) + [service_type]
            raise CircularDependencyError(chain)

        self._resolving.add(service_type)
        try:
            if reg.instance is not None:
                return reg.instance

            if reg.factory is not None:
                try:
                    return reg.factory(self)
                except (
                    ServiceNotFoundError,
                    CircularDependencyError,
                    ServiceResolutionError,
                    ScopeError,
                ):
                    raise
                except Exception as exc:
                    raise ServiceResolutionError(
                        service_type,
                        f"factory raised {type(exc).__name__}: {exc}",
                    ) from exc

            return self._construct(reg.concrete_type, service_type)

        except (ServiceNotFoundError, CircularDependencyError, ServiceResolutionError, ScopeError):
            raise
        except Exception as exc:
            raise ServiceResolutionError(service_type, str(exc)) from exc
        finally:
            self._resolving.discard(service_type)

    def _construct(self, impl_type: type, service_type: type) -> Any:
        """Instantiate *impl_type* via constructor injection.

        Inspects ``__init__`` parameters and resolves each typed dependency
        recursively through :meth:`resolve`.  Parameters with no type
        annotation are skipped (they must have defaults, or Python will raise
        at construction time).

        Uses :func:`typing.get_type_hints` to resolve string annotations
        produced by ``from __future__ import annotations`` (PEP 563).

        Args:
            impl_type: The concrete class to instantiate.
            service_type: The logical service type (used in error messages).

        Returns:
            Constructed instance of *impl_type*.

        Raises:
            ServiceResolutionError: If inspection or instantiation fails.
        """
        try:
            sig = inspect.signature(impl_type.__init__)
        except (ValueError, TypeError) as exc:
            raise ServiceResolutionError(
                service_type,
                f"cannot inspect constructor of '{impl_type.__qualname__}': {exc}",
            ) from exc

        # Resolve string annotations (handles `from __future__ import annotations`
        # and quoted forward references such as `"MyClass"`).
        try:
            resolved_hints: dict[str, Any] = typing.get_type_hints(impl_type.__init__)
        except Exception:
            resolved_hints = {}

        kwargs: dict[str, Any] = {}
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            # Prefer the fully-resolved type from get_type_hints; fall back to
            # the raw annotation (which may be a string or empty sentinel).
            annotation = resolved_hints.get(param_name, param.annotation)
            if annotation is inspect.Parameter.empty:
                # No type hint — skip; constructor must provide a default.
                continue

            if annotation in self._registrations:
                kwargs[param_name] = self.resolve(annotation)
            # else: no registration for this annotation — let the constructor
            # use its default, or raise naturally if no default exists.

        try:
            return impl_type(**kwargs)
        except Exception as exc:
            raise ServiceResolutionError(
                service_type,
                f"constructor of '{impl_type.__qualname__}' raised "
                f"{type(exc).__name__}: {exc}",
            ) from exc
