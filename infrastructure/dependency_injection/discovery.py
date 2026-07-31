"""Automatic service discovery for the RKGB Dependency Injection Framework.

:class:`ServiceDiscovery` scans Python packages and modules for classes
decorated with :func:`~.decorators.injectable` (or its shorthands) and
auto-registers them into a :class:`~.service_collection.ServiceCollection`.

This eliminates manual registration boilerplate for well-categorised
components such as command handlers, query handlers, validators, and pipeline
stages.

Example::

    from infrastructure.dependency_injection.discovery import ServiceDiscovery

    discovery = ServiceDiscovery()
    discovery.scan_package("application.command_handlers", services)
    discovery.scan_package("application.query_handlers", services)
    discovery.scan_package("application.validators", services)

    print(f"Auto-registered {len(discovery.discovered)} classes")
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from types import ModuleType
from typing import Any

from infrastructure.dependency_injection.decorators import (
    get_lifetime,
    get_service_type,
    is_injectable,
)
from infrastructure.dependency_injection.lifetimes import ServiceLifetime
from infrastructure.dependency_injection.service_collection import ServiceCollection


class ServiceDiscovery:
    """Scans packages/modules and auto-registers ``@injectable`` classes.

    Discovered classes are registered only once, even if the same module
    appears in multiple scan calls.  Classes already registered in the
    collection are silently skipped (discovery does not override explicit
    registrations).

    Attributes:
        discovered: Ordered list of all classes registered by this instance
            across all scans.
    """

    def __init__(self) -> None:
        self._discovered: list[type] = []

    def scan_package(
        self,
        package_name: str,
        services: ServiceCollection,
        *,
        recursive: bool = True,
    ) -> "ServiceDiscovery":
        """Scan a Python package and register all ``@injectable`` classes.

        Packages not yet implemented (import fails with :class:`ImportError`)
        are silently skipped — this allows discovery to be configured
        ahead of the full implementation.

        Args:
            package_name: Dot-separated package name
                (e.g. ``"application.command_handlers"``).
            services: The collection to register discovered classes into.
            recursive: When ``True`` (default), sub-packages are also scanned.

        Returns:
            Self for fluent chaining.

        Example::

            discovery.scan_package("application.handlers", services, recursive=True)
        """
        try:
            package = importlib.import_module(package_name)
        except ImportError:
            return self  # Package not yet implemented; skip gracefully.

        self._scan_module(package, services)

        if recursive and hasattr(package, "__path__"):
            for _finder, modname, _ispkg in pkgutil.walk_packages(
                path=package.__path__,
                prefix=f"{package.__name__}.",
                onerror=lambda _: None,
            ):
                try:
                    mod = importlib.import_module(modname)
                    self._scan_module(mod, services)
                except ImportError:
                    pass

        return self

    def scan_module(
        self,
        module: ModuleType,
        services: ServiceCollection,
    ) -> "ServiceDiscovery":
        """Scan a single already-imported module for ``@injectable`` classes.

        Args:
            module: An already-imported :class:`~types.ModuleType`.
            services: The collection to register into.

        Returns:
            Self for fluent chaining.
        """
        self._scan_module(module, services)
        return self

    @property
    def discovered(self) -> list[type]:
        """Return all injectable classes registered across all scans (in order).

        Returns:
            Ordered list of registered implementation types.
        """
        return list(self._discovered)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _scan_module(self, module: ModuleType, services: ServiceCollection) -> None:
        for _name, obj in inspect.getmembers(module, inspect.isclass):
            if not is_injectable(obj):
                continue
            if obj in self._discovered:
                continue  # Already registered by a previous scan.

            lifetime = get_lifetime(obj)
            abstract_type = get_service_type(obj) or obj

            # Respect explicit registrations — never override them.
            if services.has_registration(abstract_type):
                continue

            _register_class(services, abstract_type, obj, lifetime)
            self._discovered.append(obj)


# ---------------------------------------------------------------------------
# Internal registration helper
# ---------------------------------------------------------------------------


def _register_class(
    services: ServiceCollection,
    service_type: type,
    implementation_type: type,
    lifetime: Any,
) -> None:
    """Register *implementation_type* under *service_type* with *lifetime*.

    When *service_type* is the same as *implementation_type*, ``None`` is
    passed as the implementation (the collection will use the service type
    directly).

    Args:
        services: Target collection.
        service_type: Abstract type to register as.
        implementation_type: Concrete class to instantiate.
        lifetime: :class:`~.lifetimes.ServiceLifetime` value.
    """
    impl: type | None = implementation_type if implementation_type is not service_type else None

    if lifetime is ServiceLifetime.SINGLETON:
        services.add_singleton(service_type, impl)
    elif lifetime is ServiceLifetime.SCOPED:
        services.add_scoped(service_type, impl)
    else:
        services.add_transient(service_type, impl)
