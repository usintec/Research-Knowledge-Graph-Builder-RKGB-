"""Protocols (interfaces) for the RKGB Dependency Injection Framework.

All framework contracts are defined as :pep:`544` ``Protocol`` classes so that
consumers can depend on abstractions rather than concrete types.  This enables
clean testing (substitute any compatible object) and future replacement of the
underlying implementation.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class IServiceProvider(Protocol):
    """Contract for resolving services from the DI container at runtime."""

    def resolve(self, service_type: type) -> Any:
        """Resolve the given service type.

        Args:
            service_type: The abstract or concrete type to resolve.

        Returns:
            A fully constructed instance with all dependencies injected.

        Raises:
            ServiceNotFoundError: If the type is not registered.
            CircularDependencyError: If a circular dependency is detected.
            ServiceResolutionError: If construction fails.
        """
        ...

    def try_resolve(self, service_type: type) -> Any | None:
        """Resolve a service, returning ``None`` if not registered.

        Args:
            service_type: The type to resolve.

        Returns:
            Resolved instance, or ``None``.
        """
        ...

    def create_scope(self) -> "IServiceScope":
        """Create a child scope for scoped service resolution.

        Returns:
            A new :class:`IServiceScope` that shares singleton instances with
            the parent but maintains its own scoped instance cache.
        """
        ...


@runtime_checkable
class IServiceScope(Protocol):
    """A bounded execution scope for scoped service resolution.

    Scoped services created inside this scope are shared within the scope and
    discarded when the scope exits.  Singleton services are still shared with
    the parent provider.

    Typical usage::

        with provider.create_scope() as scoped_provider:
            ctx = scoped_provider.resolve(PipelineContext)
            handler = scoped_provider.resolve(ICommandHandler)
    """

    def __enter__(self) -> IServiceProvider:
        """Enter the scope and return its provider."""
        ...

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the scope, disposing all scoped instances."""
        ...

    @property
    def provider(self) -> IServiceProvider:
        """Return the scoped :class:`IServiceProvider`."""
        ...


class IServiceCollection(Protocol):
    """Contract for building service registrations.

    The collection describes *what* to register; it does not perform
    resolution.  Call ``build_provider()`` to obtain a :class:`IServiceProvider`.
    """

    def add_singleton(
        self,
        service_type: type,
        implementation_type: type | None = None,
        *,
        factory: Any | None = None,
        instance: Any | None = None,
        replace: bool = False,
    ) -> "IServiceCollection":
        """Register a singleton service.

        Args:
            service_type: The abstract type consumers depend on.
            implementation_type: Concrete class to instantiate. Defaults to
                ``service_type`` if omitted.
            factory: ``(IServiceProvider) -> instance`` callable. Takes
                precedence over ``implementation_type``.
            instance: Pre-built instance. Stored directly; no construction.
            replace: If ``True``, silently replaces an existing registration.

        Returns:
            Self for fluent chaining.
        """
        ...

    def add_scoped(
        self,
        service_type: type,
        implementation_type: type | None = None,
        *,
        factory: Any | None = None,
        replace: bool = False,
    ) -> "IServiceCollection":
        """Register a scoped service.

        Args:
            service_type: The abstract type consumers depend on.
            implementation_type: Concrete class to instantiate.
            factory: ``(IServiceProvider) -> instance`` callable.
            replace: If ``True``, silently replaces an existing registration.

        Returns:
            Self for fluent chaining.
        """
        ...

    def add_transient(
        self,
        service_type: type,
        implementation_type: type | None = None,
        *,
        factory: Any | None = None,
        replace: bool = False,
    ) -> "IServiceCollection":
        """Register a transient service.

        Args:
            service_type: The abstract type consumers depend on.
            implementation_type: Concrete class to instantiate.
            factory: ``(IServiceProvider) -> instance`` callable.
            replace: If ``True``, silently replaces an existing registration.

        Returns:
            Self for fluent chaining.
        """
        ...


class IRegistrationModule(Protocol):
    """Contract for modular, self-contained service registration units.

    Each registration module is responsible for one concern and registers
    only its own services.  The :class:`~..composition_root.CompositionRoot`
    applies modules in dependency order.

    Example implementation::

        class LoggingModule:
            def __init__(self, logging_manager: LoggingManager) -> None:
                self._manager = logging_manager

            def register(self, services: IServiceCollection) -> None:
                services.add_singleton(LoggingManager, instance=self._manager)
                services.add_singleton(
                    LoggerFactory,
                    factory=lambda p: p.resolve(LoggingManager).factory,
                )
    """

    def register(self, services: IServiceCollection) -> None:
        """Register services into the provided collection.

        Args:
            services: The :class:`IServiceCollection` to register into.
        """
        ...
