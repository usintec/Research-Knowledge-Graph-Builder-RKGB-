"""DIContainer — central dependency injection container.

The container is the primary API surface for application code that needs to
register *and* resolve services.  It delegates registration to an internal
:class:`~.service_collection.ServiceCollection` and resolution to a
:class:`~.service_provider.ServiceProvider` that is built on demand.

Typical usage in a composition root::

    container = DIContainer()
    container.add_singleton(IRepository, Neo4jRepository)
    container.add_transient(IValidator, DocumentValidator)
    container.add_module(LoggingModule(logging_manager))

    provider = container.build()
    repo = provider.resolve(IRepository)
"""

from __future__ import annotations

from typing import Any, Callable

from infrastructure.dependency_injection.service_collection import ServiceCollection
from infrastructure.dependency_injection.service_provider import ServiceProvider


class DIContainer:
    """Central dependency injection container.

    Combines :class:`~.service_collection.ServiceCollection` for registration
    and :class:`~.service_provider.ServiceProvider` for resolution into a
    single, convenient entry point.

    The container separates the *registration* phase (configuring what to
    build) from the *resolution* phase (actually building and managing
    instances).  :meth:`build` marks the boundary: registrations added after
    ``build()`` do not affect the provider.

    Example::

        container = DIContainer()

        # Registration phase
        container.add_singleton(ConfigManager, instance=config_manager)
        container.add_singleton(LoggerFactory,
            factory=lambda p: p.resolve(LoggingManager).factory)
        container.add_transient(IValidator, DocumentValidator)
        container.add_module(RepositoryModule())

        # Resolution phase
        provider = container.build()
        validator = provider.resolve(IValidator)
    """

    def __init__(self) -> None:
        self._collection = ServiceCollection()
        self._provider: ServiceProvider | None = None

    # ------------------------------------------------------------------
    # Registration — delegates to ServiceCollection
    # ------------------------------------------------------------------

    def add_singleton(
        self,
        service_type: type,
        implementation_type: type | None = None,
        *,
        factory: Callable[..., Any] | None = None,
        instance: Any | None = None,
        replace: bool = False,
    ) -> "DIContainer":
        """Register a singleton service.

        Args:
            service_type: The abstract type consumers depend on.
            implementation_type: Concrete class to instantiate.
            factory: ``(IServiceProvider) -> instance`` callable.
            instance: Pre-built object stored directly.
            replace: Override an existing registration when ``True``.

        Returns:
            Self for fluent chaining.
        """
        self._collection.add_singleton(
            service_type,
            implementation_type,
            factory=factory,
            instance=instance,
            replace=replace,
        )
        return self

    def add_scoped(
        self,
        service_type: type,
        implementation_type: type | None = None,
        *,
        factory: Callable[..., Any] | None = None,
        replace: bool = False,
    ) -> "DIContainer":
        """Register a scoped service.

        Args:
            service_type: The abstract type consumers depend on.
            implementation_type: Concrete class to instantiate.
            factory: ``(IServiceProvider) -> instance`` callable.
            replace: Override an existing registration when ``True``.

        Returns:
            Self for fluent chaining.
        """
        self._collection.add_scoped(
            service_type,
            implementation_type,
            factory=factory,
            replace=replace,
        )
        return self

    def add_transient(
        self,
        service_type: type,
        implementation_type: type | None = None,
        *,
        factory: Callable[..., Any] | None = None,
        replace: bool = False,
    ) -> "DIContainer":
        """Register a transient service.

        Args:
            service_type: The abstract type consumers depend on.
            implementation_type: Concrete class to instantiate.
            factory: ``(IServiceProvider) -> instance`` callable.
            replace: Override an existing registration when ``True``.

        Returns:
            Self for fluent chaining.
        """
        self._collection.add_transient(
            service_type,
            implementation_type,
            factory=factory,
            replace=replace,
        )
        return self

    def add_module(self, module: Any) -> "DIContainer":
        """Apply a registration module to this container.

        The *module* must expose a ``register(services)`` method.

        Args:
            module: Any object implementing
                :class:`~.interfaces.IRegistrationModule`.

        Returns:
            Self for fluent chaining.
        """
        self._collection.add_module(module)
        return self

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self) -> ServiceProvider:
        """Build and return the :class:`~.service_provider.ServiceProvider`.

        Creates a provider from a snapshot of the current registrations.
        Further calls to registration methods do not affect the built
        provider.  Calling ``build()`` a second time creates a fresh
        provider with the same registrations.

        Returns:
            Configured :class:`~.service_provider.ServiceProvider`.
        """
        self._provider = self._collection.build_provider()
        return self._provider

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    @property
    def collection(self) -> ServiceCollection:
        """Return the underlying :class:`~.service_collection.ServiceCollection`.

        Returns:
            The registration collection.
        """
        return self._collection

    @property
    def provider(self) -> ServiceProvider:
        """Return the built :class:`~.service_provider.ServiceProvider`.

        Returns:
            The active :class:`ServiceProvider`.

        Raises:
            RuntimeError: If :meth:`build` has not been called yet.
        """
        if self._provider is None:
            raise RuntimeError(
                "The DI container has not been built. Call container.build() first."
            )
        return self._provider

    def __len__(self) -> int:
        """Return the number of registered services."""
        return len(self._collection)
