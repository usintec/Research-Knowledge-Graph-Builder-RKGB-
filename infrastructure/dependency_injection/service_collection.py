"""ServiceCollection — fluent API for building service registrations.

The collection is the *description* phase of the DI lifecycle.  It records
what to register but performs no object construction.  Call
:meth:`build_provider` once all registrations are complete to obtain a
:class:`~.service_provider.ServiceProvider` capable of resolving them.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from infrastructure.dependency_injection.exceptions import DuplicateRegistrationError
from infrastructure.dependency_injection.lifetimes import ServiceLifetime
from infrastructure.dependency_injection.registration import ServiceRegistration

if TYPE_CHECKING:
    from infrastructure.dependency_injection.service_provider import ServiceProvider


class ServiceCollection:
    """Fluent service registration builder.

    Records registrations without performing any resolution.  Call
    :meth:`build_provider` to build the runtime :class:`ServiceProvider`.

    Example::

        from infrastructure.dependency_injection.service_collection import ServiceCollection

        services = ServiceCollection()
        services.add_singleton(IRepository, Neo4jDocumentRepository)
        services.add_transient(IValidator, DocumentValidator)
        services.add_scoped(PipelineContext)

        provider = services.build_provider()
        repo = provider.resolve(IRepository)
    """

    def __init__(self) -> None:
        self._registrations: dict[type, ServiceRegistration] = {}

    # ------------------------------------------------------------------
    # Registration — fluent API
    # ------------------------------------------------------------------

    def add_singleton(
        self,
        service_type: type,
        implementation_type: type | None = None,
        *,
        factory: Callable[..., Any] | None = None,
        instance: Any | None = None,
        replace: bool = False,
    ) -> "ServiceCollection":
        """Register *service_type* with :attr:`~ServiceLifetime.SINGLETON` lifetime.

        Args:
            service_type: The abstract type consumers depend on.
            implementation_type: Concrete class to instantiate. Defaults to
                ``service_type`` when ``None``.
            factory: ``(IServiceProvider) -> instance`` callable. Takes
                precedence over ``implementation_type``.
            instance: Pre-built object. Stored directly without construction.
                Implies ``SINGLETON`` regardless of the ``lifetime`` argument.
            replace: When ``True``, silently overrides an existing registration
                for the same ``service_type``.

        Returns:
            Self, enabling fluent chaining.

        Raises:
            DuplicateRegistrationError: If ``service_type`` is already registered
                and ``replace`` is ``False``.
        """
        return self._add(
            service_type,
            implementation_type,
            factory=factory,
            instance=instance,
            lifetime=ServiceLifetime.SINGLETON,
            replace=replace,
        )

    def add_scoped(
        self,
        service_type: type,
        implementation_type: type | None = None,
        *,
        factory: Callable[..., Any] | None = None,
        replace: bool = False,
    ) -> "ServiceCollection":
        """Register *service_type* with :attr:`~ServiceLifetime.SCOPED` lifetime.

        Args:
            service_type: The abstract type consumers depend on.
            implementation_type: Concrete class to instantiate.
            factory: ``(IServiceProvider) -> instance`` callable.
            replace: When ``True``, silently overrides an existing registration.

        Returns:
            Self, enabling fluent chaining.

        Raises:
            DuplicateRegistrationError: If already registered and ``replace=False``.
        """
        return self._add(
            service_type,
            implementation_type,
            factory=factory,
            lifetime=ServiceLifetime.SCOPED,
            replace=replace,
        )

    def add_transient(
        self,
        service_type: type,
        implementation_type: type | None = None,
        *,
        factory: Callable[..., Any] | None = None,
        replace: bool = False,
    ) -> "ServiceCollection":
        """Register *service_type* with :attr:`~ServiceLifetime.TRANSIENT` lifetime.

        Args:
            service_type: The abstract type consumers depend on.
            implementation_type: Concrete class to instantiate.
            factory: ``(IServiceProvider) -> instance`` callable.
            replace: When ``True``, silently overrides an existing registration.

        Returns:
            Self, enabling fluent chaining.

        Raises:
            DuplicateRegistrationError: If already registered and ``replace=False``.
        """
        return self._add(
            service_type,
            implementation_type,
            factory=factory,
            lifetime=ServiceLifetime.TRANSIENT,
            replace=replace,
        )

    def add_module(self, module: Any) -> "ServiceCollection":
        """Apply a registration module to this collection.

        The *module* must expose a ``register(services: ServiceCollection)``
        method.  After the call, all services the module registers are
        available in this collection.

        Args:
            module: Any object implementing :class:`~.interfaces.IRegistrationModule`.

        Returns:
            Self, enabling fluent chaining.
        """
        module.register(self)
        return self

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def has_registration(self, service_type: type) -> bool:
        """Return ``True`` if *service_type* already has a registration.

        Args:
            service_type: The type to check.

        Returns:
            ``bool``.
        """
        return service_type in self._registrations

    @property
    def registrations(self) -> dict[type, ServiceRegistration]:
        """Snapshot of all current registrations (copied for safety).

        Returns:
            Dict mapping service type → :class:`~.registration.ServiceRegistration`.
        """
        return dict(self._registrations)

    def __len__(self) -> int:
        """Return the number of registered services."""
        return len(self._registrations)

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build_provider(self) -> "ServiceProvider":
        """Build and return a :class:`~.service_provider.ServiceProvider`.

        The provider is constructed from a snapshot of current registrations.
        Further changes to this collection do not affect the built provider.

        Returns:
            Configured :class:`~.service_provider.ServiceProvider`.
        """
        # Lazy import to avoid circular module dependency at import time.
        from infrastructure.dependency_injection.service_provider import ServiceProvider

        return ServiceProvider(dict(self._registrations))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _add(
        self,
        service_type: type,
        implementation_type: type | None,
        *,
        factory: Callable[..., Any] | None,
        instance: Any | None = None,
        lifetime: ServiceLifetime,
        replace: bool,
    ) -> "ServiceCollection":
        if service_type in self._registrations and not replace:
            raise DuplicateRegistrationError(service_type)

        self._registrations[service_type] = ServiceRegistration(
            service_type=service_type,
            implementation_type=implementation_type,
            factory=factory,
            instance=instance,
            lifetime=lifetime,
        )
        return self
