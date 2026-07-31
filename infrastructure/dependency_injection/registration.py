"""ServiceRegistration — immutable descriptor for a single DI registration.

Each registration captures everything the :class:`~.service_provider.ServiceProvider`
needs to construct and cache a service instance: the abstract type, the
concrete type or factory, and the lifetime policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from infrastructure.dependency_injection.lifetimes import ServiceLifetime


@dataclass(frozen=True)
class ServiceRegistration:
    """Immutable descriptor for one service registration.

    Resolution precedence (highest to lowest):
        1. ``instance`` — returned as-is; always treated as a singleton.
        2. ``factory`` — called with the active :class:`~.service_provider.ServiceProvider`.
        3. ``implementation_type`` — instantiated via constructor injection.
        4. ``service_type`` — used as its own concrete type when no
           ``implementation_type`` is provided.

    Attributes:
        service_type: The abstract type (interface/Protocol/ABC) that consumers
            declare as their dependency.
        lifetime: Controls how long the resolved instance is retained.
        implementation_type: The concrete class to instantiate. When ``None``,
            ``service_type`` is instantiated directly (suitable for concrete
            registrations without an abstract interface).
        factory: An optional callable ``(IServiceProvider) -> instance``.
            Takes full precedence over ``implementation_type`` when provided.
            The provider passed as the argument is the *active* provider for
            the current scope, enabling factories to resolve their own deps.
        instance: A pre-built object stored directly as the singleton value.
            When provided the ``lifetime`` is automatically coerced to
            ``SINGLETON``.
        name: Reserved for future named/keyed registrations.  Not used by the
            current resolver.
    """

    service_type: type
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    implementation_type: type | None = None
    factory: Callable[..., Any] | None = None
    instance: Any | None = None
    name: str | None = None

    def __post_init__(self) -> None:
        # A pre-built instance is always singleton — coerce silently.
        if self.instance is not None and self.lifetime is not ServiceLifetime.SINGLETON:
            object.__setattr__(self, "lifetime", ServiceLifetime.SINGLETON)

    @property
    def concrete_type(self) -> type:
        """Return the implementation type, falling back to the service type.

        Returns:
            The class that will be instantiated during constructor injection.
        """
        return self.implementation_type or self.service_type
