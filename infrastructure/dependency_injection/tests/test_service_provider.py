"""Unit tests for ServiceProvider.

Covers:
    * Basic resolution.
    * Singleton lifetime caching.
    * Transient lifetime (fresh instance per resolution).
    * Scoped lifetime isolation.
    * Constructor injection (typed parameters resolved automatically).
    * Factory registration.
    * Instance registration.
    * ServiceNotFoundError for unregistered types.
    * CircularDependencyError detection.
    * ScopeError when resolving scoped services outside a scope.
    * try_resolve returns None on missing.
"""

from __future__ import annotations

import pytest

from infrastructure.dependency_injection.exceptions import (
    CircularDependencyError,
    ScopeError,
    ServiceNotFoundError,
    ServiceResolutionError,
)
from infrastructure.dependency_injection.lifetimes import ServiceLifetime
from infrastructure.dependency_injection.registration import ServiceRegistration
from infrastructure.dependency_injection.service_provider import ServiceProvider


# ---------------------------------------------------------------------------
# Helper types
# ---------------------------------------------------------------------------


class ILogger:
    """Fake logger interface."""


class ConcreteLogger(ILogger):
    """Simple concrete logger — no deps."""


class IRepository:
    """Fake repository interface."""


class ConcreteRepository(IRepository):
    def __init__(self, logger: ILogger) -> None:
        self.logger = logger


class CircularA:
    def __init__(self, b: "CircularB") -> None:
        self.b = b


class CircularB:
    def __init__(self, a: "CircularA") -> None:
        self.a = a


class ScopedService:
    """A service that should be scoped."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_provider(*regs: ServiceRegistration) -> ServiceProvider:
    return ServiceProvider({r.service_type: r for r in regs})


def _singleton(svc: type, impl: type | None = None) -> ServiceRegistration:
    return ServiceRegistration(service_type=svc, implementation_type=impl, lifetime=ServiceLifetime.SINGLETON)


def _transient(svc: type, impl: type | None = None) -> ServiceRegistration:
    return ServiceRegistration(service_type=svc, implementation_type=impl, lifetime=ServiceLifetime.TRANSIENT)


def _scoped(svc: type, impl: type | None = None) -> ServiceRegistration:
    return ServiceRegistration(service_type=svc, implementation_type=impl, lifetime=ServiceLifetime.SCOPED)


# ---------------------------------------------------------------------------
# Basic resolution
# ---------------------------------------------------------------------------


class TestBasicResolution:
    def test_resolve_concrete_type(self) -> None:
        provider = _make_provider(_singleton(ConcreteLogger))
        instance = provider.resolve(ConcreteLogger)
        assert isinstance(instance, ConcreteLogger)

    def test_resolve_interface_to_impl(self) -> None:
        provider = _make_provider(_singleton(ILogger, ConcreteLogger))
        instance = provider.resolve(ILogger)
        assert isinstance(instance, ConcreteLogger)

    def test_unregistered_raises_service_not_found(self) -> None:
        provider = _make_provider()
        with pytest.raises(ServiceNotFoundError) as exc_info:
            provider.resolve(ConcreteLogger)
        assert exc_info.value.service_type is ConcreteLogger

    def test_try_resolve_returns_none_when_not_registered(self) -> None:
        provider = _make_provider()
        assert provider.try_resolve(ConcreteLogger) is None

    def test_try_resolve_returns_instance_when_registered(self) -> None:
        provider = _make_provider(_singleton(ConcreteLogger))
        result = provider.try_resolve(ConcreteLogger)
        assert isinstance(result, ConcreteLogger)


# ---------------------------------------------------------------------------
# Singleton lifetime
# ---------------------------------------------------------------------------


class TestSingletonLifetime:
    def test_singleton_returns_same_instance(self) -> None:
        provider = _make_provider(_singleton(ConcreteLogger))
        a = provider.resolve(ConcreteLogger)
        b = provider.resolve(ConcreteLogger)
        assert a is b

    def test_singleton_instance_registration(self) -> None:
        obj = ConcreteLogger()
        reg = ServiceRegistration(service_type=ILogger, instance=obj)
        provider = _make_provider(reg)
        resolved = provider.resolve(ILogger)
        assert resolved is obj


# ---------------------------------------------------------------------------
# Transient lifetime
# ---------------------------------------------------------------------------


class TestTransientLifetime:
    def test_transient_returns_new_instance_each_time(self) -> None:
        provider = _make_provider(_transient(ConcreteLogger))
        a = provider.resolve(ConcreteLogger)
        b = provider.resolve(ConcreteLogger)
        assert a is not b


# ---------------------------------------------------------------------------
# Scoped lifetime
# ---------------------------------------------------------------------------


class TestScopedLifetime:
    def test_scoped_raises_outside_scope(self) -> None:
        provider = _make_provider(_scoped(ScopedService))
        with pytest.raises(ScopeError):
            provider.resolve(ScopedService)

    def test_scoped_returns_same_instance_within_scope(self) -> None:
        provider = _make_provider(_scoped(ScopedService))
        with provider.create_scope() as scoped:
            a = scoped.resolve(ScopedService)
            b = scoped.resolve(ScopedService)
        assert a is b

    def test_scoped_returns_different_instances_across_scopes(self) -> None:
        provider = _make_provider(_scoped(ScopedService))
        with provider.create_scope() as scope1:
            a = scope1.resolve(ScopedService)
        with provider.create_scope() as scope2:
            b = scope2.resolve(ScopedService)
        assert a is not b

    def test_singleton_shared_across_scopes(self) -> None:
        provider = _make_provider(_singleton(ConcreteLogger))
        with provider.create_scope() as scope1:
            a = scope1.resolve(ConcreteLogger)
        with provider.create_scope() as scope2:
            b = scope2.resolve(ConcreteLogger)
        assert a is b

    def test_scope_clears_on_exit(self) -> None:
        provider = _make_provider(_scoped(ScopedService))
        with provider.create_scope() as scoped:
            instance = scoped.resolve(ScopedService)
        # After scope exit resolving again in a new scope creates a new obj.
        with provider.create_scope() as scoped2:
            new_instance = scoped2.resolve(ScopedService)
        assert instance is not new_instance


# ---------------------------------------------------------------------------
# Constructor injection
# ---------------------------------------------------------------------------


class TestConstructorInjection:
    def test_dependencies_injected_automatically(self) -> None:
        provider = _make_provider(
            _singleton(ILogger, ConcreteLogger),
            _singleton(IRepository, ConcreteRepository),
        )
        repo = provider.resolve(IRepository)
        assert isinstance(repo, ConcreteRepository)
        assert isinstance(repo.logger, ConcreteLogger)

    def test_nested_injection(self) -> None:
        """IRepository → ConcreteLogger (ILogger) resolved transitively."""
        provider = _make_provider(
            _transient(ILogger, ConcreteLogger),
            _transient(IRepository, ConcreteRepository),
        )
        repo = provider.resolve(IRepository)
        assert isinstance(repo.logger, ConcreteLogger)


# ---------------------------------------------------------------------------
# Factory registration
# ---------------------------------------------------------------------------


class TestFactoryRegistration:
    def test_factory_called_to_produce_instance(self) -> None:
        sentinel = ConcreteLogger()
        reg = ServiceRegistration(
            service_type=ILogger,
            factory=lambda p: sentinel,
            lifetime=ServiceLifetime.SINGLETON,
        )
        provider = _make_provider(reg)
        resolved = provider.resolve(ILogger)
        assert resolved is sentinel

    def test_factory_receives_provider(self) -> None:
        captured: list[object] = []
        reg = ServiceRegistration(
            service_type=ILogger,
            factory=lambda p: captured.append(p) or ConcreteLogger(),
            lifetime=ServiceLifetime.TRANSIENT,
        )
        provider = _make_provider(reg)
        provider.resolve(ILogger)
        assert captured[0] is provider

    def test_factory_exception_wrapped_as_resolution_error(self) -> None:
        def bad_factory(p: object) -> object:
            raise ValueError("boom")

        reg = ServiceRegistration(
            service_type=ILogger,
            factory=bad_factory,
            lifetime=ServiceLifetime.TRANSIENT,
        )
        provider = _make_provider(reg)
        with pytest.raises(ServiceResolutionError):
            provider.resolve(ILogger)


# ---------------------------------------------------------------------------
# Circular dependency detection
# ---------------------------------------------------------------------------


class TestCircularDependencyDetection:
    def test_circular_dependency_raises(self) -> None:
        provider = _make_provider(
            _singleton(CircularA),
            _singleton(CircularB),
        )
        with pytest.raises(CircularDependencyError) as exc_info:
            provider.resolve(CircularA)
        # The chain must include both types.
        type_names = [t.__qualname__ for t in exc_info.value.chain]
        assert any("CircularA" in n for n in type_names)
        assert any("CircularB" in n for n in type_names)
