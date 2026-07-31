"""Unit tests for ServiceCollection.

Covers:
    * Singleton / scoped / transient registration.
    * Factory and instance registration.
    * DuplicateRegistrationError and replace=True.
    * add_module delegation.
    * has_registration, registrations snapshot, __len__.
    * build_provider returns a working ServiceProvider.
"""

from __future__ import annotations

import pytest

from infrastructure.dependency_injection.exceptions import DuplicateRegistrationError
from infrastructure.dependency_injection.lifetimes import ServiceLifetime
from infrastructure.dependency_injection.service_collection import ServiceCollection
from infrastructure.dependency_injection.service_provider import ServiceProvider


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class IService:
    """Fake interface."""


class ConcreteService(IService):
    """Concrete implementation."""


class AnotherService:
    """A separate concrete service."""


class SimpleModule:
    """A minimal registration module."""

    def register(self, services: ServiceCollection) -> None:
        services.add_singleton(AnotherService)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


class TestServiceCollectionRegistration:
    def test_add_singleton_stores_registration(self) -> None:
        services = ServiceCollection()
        services.add_singleton(IService, ConcreteService)

        assert services.has_registration(IService)
        reg = services.registrations[IService]
        assert reg.lifetime is ServiceLifetime.SINGLETON
        assert reg.concrete_type is ConcreteService

    def test_add_scoped_stores_registration(self) -> None:
        services = ServiceCollection()
        services.add_scoped(IService, ConcreteService)

        reg = services.registrations[IService]
        assert reg.lifetime is ServiceLifetime.SCOPED

    def test_add_transient_stores_registration(self) -> None:
        services = ServiceCollection()
        services.add_transient(IService, ConcreteService)

        reg = services.registrations[IService]
        assert reg.lifetime is ServiceLifetime.TRANSIENT

    def test_add_singleton_with_no_impl_uses_service_type(self) -> None:
        services = ServiceCollection()
        services.add_singleton(ConcreteService)

        reg = services.registrations[ConcreteService]
        assert reg.concrete_type is ConcreteService

    def test_add_singleton_with_instance(self) -> None:
        obj = ConcreteService()
        services = ServiceCollection()
        services.add_singleton(IService, instance=obj)

        reg = services.registrations[IService]
        assert reg.instance is obj
        # Instance implies singleton regardless of lifetime arg.
        assert reg.lifetime is ServiceLifetime.SINGLETON

    def test_add_singleton_with_factory(self) -> None:
        factory = lambda p: ConcreteService()  # noqa: E731
        services = ServiceCollection()
        services.add_singleton(IService, factory=factory)

        reg = services.registrations[IService]
        assert reg.factory is factory

    def test_duplicate_raises_error(self) -> None:
        services = ServiceCollection()
        services.add_singleton(IService, ConcreteService)

        with pytest.raises(DuplicateRegistrationError) as exc_info:
            services.add_singleton(IService, ConcreteService)

        assert exc_info.value.service_type is IService

    def test_replace_true_overrides_existing(self) -> None:
        services = ServiceCollection()
        services.add_singleton(IService, ConcreteService)
        services.add_transient(IService, ConcreteService, replace=True)

        reg = services.registrations[IService]
        assert reg.lifetime is ServiceLifetime.TRANSIENT

    def test_fluent_chaining_returns_self(self) -> None:
        services = ServiceCollection()
        result = services.add_singleton(IService, ConcreteService)
        assert result is services

    def test_has_registration_false_when_absent(self) -> None:
        services = ServiceCollection()
        assert not services.has_registration(IService)

    def test_len_reflects_registration_count(self) -> None:
        services = ServiceCollection()
        assert len(services) == 0
        services.add_singleton(IService, ConcreteService)
        assert len(services) == 1
        services.add_transient(AnotherService)
        assert len(services) == 2

    def test_registrations_returns_snapshot(self) -> None:
        services = ServiceCollection()
        services.add_singleton(IService, ConcreteService)
        snapshot = services.registrations

        # Mutating the snapshot does not affect the collection.
        del snapshot[IService]
        assert services.has_registration(IService)

    def test_add_module_applies_registrations(self) -> None:
        services = ServiceCollection()
        services.add_module(SimpleModule())
        assert services.has_registration(AnotherService)

    def test_add_module_returns_self(self) -> None:
        services = ServiceCollection()
        result = services.add_module(SimpleModule())
        assert result is services


# ---------------------------------------------------------------------------
# Build provider
# ---------------------------------------------------------------------------


class TestBuildProvider:
    def test_build_provider_returns_service_provider(self) -> None:
        services = ServiceCollection()
        services.add_singleton(ConcreteService)
        provider = services.build_provider()
        assert isinstance(provider, ServiceProvider)

    def test_built_provider_can_resolve_registered_service(self) -> None:
        services = ServiceCollection()
        services.add_singleton(ConcreteService)
        provider = services.build_provider()
        instance = provider.resolve(ConcreteService)
        assert isinstance(instance, ConcreteService)
