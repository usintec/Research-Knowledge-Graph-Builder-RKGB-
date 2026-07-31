"""Unit tests for DIContainer.

Covers:
    * Registration delegation to ServiceCollection.
    * build() returns a working ServiceProvider.
    * provider property raises before build().
    * add_module applies modules.
    * collection property is accessible.
    * __len__ reflects registration count.
"""

from __future__ import annotations

import pytest

from infrastructure.dependency_injection.container import DIContainer
from infrastructure.dependency_injection.exceptions import DuplicateRegistrationError
from infrastructure.dependency_injection.service_provider import ServiceProvider


# ---------------------------------------------------------------------------
# Helper types
# ---------------------------------------------------------------------------


class IService:
    """Fake interface."""


class ServiceA(IService):
    """Concrete implementation A — no deps."""


class ServiceB:
    """Another concrete service — no deps."""


class SimpleModule:
    """Minimal registration module."""

    def register(self, services: object) -> None:
        services.add_transient(ServiceB)  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


class TestDIContainerRegistration:
    def test_add_singleton_registers_service(self) -> None:
        container = DIContainer()
        container.add_singleton(IService, ServiceA)
        assert container.collection.has_registration(IService)

    def test_add_scoped_registers_service(self) -> None:
        container = DIContainer()
        container.add_scoped(IService, ServiceA)
        assert container.collection.has_registration(IService)

    def test_add_transient_registers_service(self) -> None:
        container = DIContainer()
        container.add_transient(IService, ServiceA)
        assert container.collection.has_registration(IService)

    def test_add_singleton_with_instance(self) -> None:
        obj = ServiceA()
        container = DIContainer()
        container.add_singleton(IService, instance=obj)
        reg = container.collection.registrations[IService]
        assert reg.instance is obj

    def test_add_singleton_with_factory(self) -> None:
        factory = lambda p: ServiceA()  # noqa: E731
        container = DIContainer()
        container.add_singleton(IService, factory=factory)
        reg = container.collection.registrations[IService]
        assert reg.factory is factory

    def test_duplicate_raises_error(self) -> None:
        container = DIContainer()
        container.add_singleton(IService, ServiceA)
        with pytest.raises(DuplicateRegistrationError):
            container.add_singleton(IService, ServiceA)

    def test_replace_overrides_registration(self) -> None:
        container = DIContainer()
        container.add_singleton(IService, ServiceA)
        container.add_transient(IService, ServiceA, replace=True)
        from infrastructure.dependency_injection.lifetimes import ServiceLifetime
        reg = container.collection.registrations[IService]
        assert reg.lifetime is ServiceLifetime.TRANSIENT

    def test_fluent_chaining(self) -> None:
        container = DIContainer()
        result = container.add_singleton(IService, ServiceA).add_transient(ServiceB)
        assert result is container

    def test_add_module_applies_registrations(self) -> None:
        container = DIContainer()
        container.add_module(SimpleModule())
        assert container.collection.has_registration(ServiceB)

    def test_add_module_returns_self(self) -> None:
        container = DIContainer()
        result = container.add_module(SimpleModule())
        assert result is container

    def test_len_reflects_count(self) -> None:
        container = DIContainer()
        assert len(container) == 0
        container.add_singleton(ServiceA)
        assert len(container) == 1


# ---------------------------------------------------------------------------
# Build and resolve
# ---------------------------------------------------------------------------


class TestDIContainerBuild:
    def test_build_returns_service_provider(self) -> None:
        container = DIContainer()
        container.add_singleton(ServiceA)
        provider = container.build()
        assert isinstance(provider, ServiceProvider)

    def test_built_provider_resolves_services(self) -> None:
        container = DIContainer()
        container.add_singleton(ServiceA)
        provider = container.build()
        instance = provider.resolve(ServiceA)
        assert isinstance(instance, ServiceA)

    def test_provider_property_raises_before_build(self) -> None:
        container = DIContainer()
        with pytest.raises(RuntimeError, match="not been built"):
            _ = container.provider

    def test_provider_property_returns_provider_after_build(self) -> None:
        container = DIContainer()
        container.add_singleton(ServiceA)
        provider = container.build()
        assert container.provider is provider

    def test_end_to_end_singleton_resolution(self) -> None:
        container = DIContainer()
        instance = ServiceA()
        container.add_singleton(IService, instance=instance)
        provider = container.build()
        resolved = provider.resolve(IService)
        assert resolved is instance
