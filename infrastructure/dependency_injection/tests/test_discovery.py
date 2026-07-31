"""Unit tests for ServiceDiscovery.

Covers:
    * @injectable, @singleton, @scoped, @transient decorators attach metadata.
    * is_injectable / get_lifetime / get_service_type helpers.
    * ServiceDiscovery.scan_module registers @injectable classes.
    * Correct lifetime is used per decorator.
    * service_type override registers under the abstract type.
    * Already-discovered classes are not registered twice.
    * Classes already in the collection are not overridden.
    * Non-injectable classes are skipped.
    * scan_package on missing package silently succeeds.
"""

from __future__ import annotations

import types

import pytest

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
from infrastructure.dependency_injection.lifetimes import ServiceLifetime
from infrastructure.dependency_injection.service_collection import ServiceCollection


# ---------------------------------------------------------------------------
# Decorator tests
# ---------------------------------------------------------------------------


class TestInjectableDecorator:
    def test_injectable_marks_class(self) -> None:
        @injectable(ServiceLifetime.SINGLETON)
        class MyService:
            pass

        assert is_injectable(MyService)

    def test_get_lifetime_returns_configured_lifetime(self) -> None:
        @injectable(ServiceLifetime.TRANSIENT)
        class MyService:
            pass

        assert get_lifetime(MyService) is ServiceLifetime.TRANSIENT

    def test_singleton_shorthand(self) -> None:
        @singleton()
        class MySingleton:
            pass

        assert get_lifetime(MySingleton) is ServiceLifetime.SINGLETON

    def test_scoped_shorthand(self) -> None:
        @scoped()
        class MyScoped:
            pass

        assert get_lifetime(MyScoped) is ServiceLifetime.SCOPED

    def test_transient_shorthand(self) -> None:
        @transient()
        class MyTransient:
            pass

        assert get_lifetime(MyTransient) is ServiceLifetime.TRANSIENT

    def test_service_type_override(self) -> None:
        class IAbstract:
            pass

        @singleton(service_type=IAbstract)
        class ConcreteImpl(IAbstract):
            pass

        assert get_service_type(ConcreteImpl) is IAbstract

    def test_get_service_type_none_when_not_set(self) -> None:
        @singleton()
        class MyService:
            pass

        assert get_service_type(MyService) is None

    def test_is_injectable_false_for_plain_class(self) -> None:
        class PlainClass:
            pass

        assert not is_injectable(PlainClass)

    def test_decorator_does_not_change_class_behaviour(self) -> None:
        @transient()
        class Counter:
            def __init__(self) -> None:
                self.count = 0

            def increment(self) -> None:
                self.count += 1

        c = Counter()
        c.increment()
        assert c.count == 1


# ---------------------------------------------------------------------------
# ServiceDiscovery tests
# ---------------------------------------------------------------------------


def _make_module(**attrs: object) -> types.ModuleType:
    """Create a synthetic module with the given attributes."""
    mod = types.ModuleType("synthetic_test_module")
    for name, value in attrs.items():
        setattr(mod, name, value)
    return mod


class TestServiceDiscovery:
    def test_scan_module_registers_injectable_class(self) -> None:
        @singleton()
        class AutoService:
            pass

        mod = _make_module(AutoService=AutoService)
        services = ServiceCollection()
        discovery = ServiceDiscovery()
        discovery.scan_module(mod, services)

        assert services.has_registration(AutoService)

    def test_scan_module_uses_correct_lifetime(self) -> None:
        @transient()
        class TransientService:
            pass

        mod = _make_module(TransientService=TransientService)
        services = ServiceCollection()
        ServiceDiscovery().scan_module(mod, services)

        reg = services.registrations[TransientService]
        assert reg.lifetime is ServiceLifetime.TRANSIENT

    def test_scan_module_registers_under_service_type(self) -> None:
        class IAbstract:
            pass

        @singleton(service_type=IAbstract)
        class ConcreteImpl(IAbstract):
            pass

        mod = _make_module(ConcreteImpl=ConcreteImpl)
        services = ServiceCollection()
        ServiceDiscovery().scan_module(mod, services)

        assert services.has_registration(IAbstract)
        assert not services.has_registration(ConcreteImpl)

    def test_scan_module_skips_non_injectable(self) -> None:
        class PlainClass:
            pass

        mod = _make_module(PlainClass=PlainClass)
        services = ServiceCollection()
        ServiceDiscovery().scan_module(mod, services)

        assert not services.has_registration(PlainClass)

    def test_scan_module_does_not_override_explicit_registration(self) -> None:
        class IAbstract:
            pass

        @singleton(service_type=IAbstract)
        class AutoImpl(IAbstract):
            pass

        class ExplicitImpl(IAbstract):
            pass

        services = ServiceCollection()
        services.add_singleton(IAbstract, ExplicitImpl)  # Explicit registration.

        mod = _make_module(AutoImpl=AutoImpl)
        ServiceDiscovery().scan_module(mod, services)

        # Explicit registration should still be in place.
        reg = services.registrations[IAbstract]
        assert reg.concrete_type is ExplicitImpl

    def test_discovered_tracks_all_found_classes(self) -> None:
        @singleton()
        class Svc1:
            pass

        @transient()
        class Svc2:
            pass

        mod = _make_module(Svc1=Svc1, Svc2=Svc2)
        services = ServiceCollection()
        discovery = ServiceDiscovery()
        discovery.scan_module(mod, services)

        assert Svc1 in discovery.discovered
        assert Svc2 in discovery.discovered

    def test_duplicate_scan_does_not_register_twice(self) -> None:
        @singleton()
        class SingleSvc:
            pass

        mod = _make_module(SingleSvc=SingleSvc)
        services = ServiceCollection()
        discovery = ServiceDiscovery()
        discovery.scan_module(mod, services)
        # Scanning the same module again — should be idempotent.
        discovery.scan_module(mod, services)

        assert discovery.discovered.count(SingleSvc) == 1

    def test_scan_package_missing_package_silently_skips(self) -> None:
        services = ServiceCollection()
        discovery = ServiceDiscovery()
        # A package that definitely does not exist — should not raise.
        discovery.scan_package("rkgb.__nonexistent_package__", services)
        assert discovery.discovered == []
