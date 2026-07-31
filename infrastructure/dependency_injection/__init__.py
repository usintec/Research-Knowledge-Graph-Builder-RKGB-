"""RKGB Dependency Injection Framework.

Provides a clean, interface-first dependency injection container for the
entire RKGB platform.  Built on SOLID and Clean Architecture principles, the
framework enforces constructor injection, explicit dependency graphs, and
fail-fast startup validation.

Quick start::

    from infrastructure.config.bootstrap import bootstrap_config
    from infrastructure.logging.bootstrap import bootstrap_logging
    from infrastructure.dependency_injection import bootstrap_container

    config   = bootstrap_config()
    logging  = bootstrap_logging(config)
    provider = bootstrap_container(config, logging)

    from infrastructure.logging import LoggerFactory
    factory = provider.resolve(LoggerFactory)

Key components:
    * :func:`bootstrap_container` — single startup entry point.
    * :class:`DIContainer` — registration + build API.
    * :class:`ServiceCollection` — fluent registration builder.
    * :class:`ServiceProvider` — runtime resolver and lifetime manager.
    * :class:`ServiceScope` — scoped service isolation.
    * :class:`CompositionRoot` — wires all platform modules.
    * :func:`injectable` / :func:`singleton` / :func:`scoped` / :func:`transient`
      — auto-discovery decorators.
    * :class:`ServiceDiscovery` — package scanner for decorated classes.
    * :func:`validate_registrations` — startup validation.

Design constraints:
    - Constructor injection only — no property injection or service locator.
    - No global singletons — all state lives inside the provider.
    - No hidden dependencies — every dependency must appear in ``__init__``.
    - Fail fast — :func:`validate_registrations` catches problems at boot time.
"""

from __future__ import annotations

from infrastructure.dependency_injection.bootstrap import bootstrap_container, build_test_container
from infrastructure.dependency_injection.composition_root import CompositionRoot
from infrastructure.dependency_injection.container import DIContainer
from infrastructure.dependency_injection.decorators import (
    get_lifetime,
    get_service_type,
    injectable,
    is_injectable,
    scoped,
    singleton,
    transient,
)
from infrastructure.dependency_injection.discovery import ServiceDiscovery
from infrastructure.dependency_injection.exceptions import (
    CircularDependencyError,
    DIError,
    DuplicateRegistrationError,
    InvalidLifetimeError,
    MissingDependencyError,
    ScopeError,
    ServiceNotFoundError,
    ServiceResolutionError,
    StartupValidationError,
)
from infrastructure.dependency_injection.interfaces import (
    IRegistrationModule,
    IServiceCollection,
    IServiceProvider,
    IServiceScope,
)
from infrastructure.dependency_injection.lifetimes import ServiceLifetime
from infrastructure.dependency_injection.registration import ServiceRegistration
from infrastructure.dependency_injection.service_collection import ServiceCollection
from infrastructure.dependency_injection.service_provider import ServiceProvider, ServiceScope
from infrastructure.dependency_injection.validators import validate_registrations

__all__ = [
    # Bootstrap
    "bootstrap_container",
    "build_test_container",
    # Core types
    "DIContainer",
    "CompositionRoot",
    "ServiceCollection",
    "ServiceProvider",
    "ServiceScope",
    "ServiceRegistration",
    "ServiceLifetime",
    "ServiceDiscovery",
    # Interfaces / Protocols
    "IServiceCollection",
    "IServiceProvider",
    "IServiceScope",
    "IRegistrationModule",
    # Decorators
    "injectable",
    "singleton",
    "scoped",
    "transient",
    "is_injectable",
    "get_lifetime",
    "get_service_type",
    # Validation
    "validate_registrations",
    # Exceptions
    "DIError",
    "ServiceNotFoundError",
    "CircularDependencyError",
    "DuplicateRegistrationError",
    "InvalidLifetimeError",
    "MissingDependencyError",
    "ServiceResolutionError",
    "ScopeError",
    "StartupValidationError",
]
