"""Unit tests for startup validators.

Covers:
    * validate_registrations passes when everything is correct.
    * Abstract implementation detected.
    * Missing required dependency detected.
    * Optional (defaulted) dependency is not flagged.
    * Circular dependency detected.
    * Singleton-captures-scoped lifetime violation detected.
    * Multiple errors collected in one shot.
"""

from __future__ import annotations

import abc

import pytest

from infrastructure.dependency_injection.exceptions import StartupValidationError
from infrastructure.dependency_injection.lifetimes import ServiceLifetime
from infrastructure.dependency_injection.registration import ServiceRegistration
from infrastructure.dependency_injection.validators import validate_registrations


# ---------------------------------------------------------------------------
# Helper types
# ---------------------------------------------------------------------------


class IAbstract(abc.ABC):
    @abc.abstractmethod
    def do(self) -> None: ...


class Concrete:
    """No dependencies."""


class NeedsConcrete:
    def __init__(self, dep: Concrete) -> None:
        self.dep = dep


class NeedsOptional:
    def __init__(self, dep: Concrete = None) -> None:  # type: ignore[assignment]
        self.dep = dep


class CycleA:
    def __init__(self, b: "CycleB") -> None: ...


class CycleB:
    def __init__(self, a: "CycleA") -> None: ...


class ScopedDep:
    """Will be registered as scoped."""


class SingletonCapture:
    def __init__(self, s: ScopedDep) -> None: ...


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _reg(
    svc: type,
    impl: type | None = None,
    lifetime: ServiceLifetime = ServiceLifetime.SINGLETON,
    *,
    factory: object = None,
    instance: object = None,
) -> ServiceRegistration:
    return ServiceRegistration(
        service_type=svc,
        implementation_type=impl,
        lifetime=lifetime,
        factory=factory,  # type: ignore[arg-type]
        instance=instance,
    )


# ---------------------------------------------------------------------------
# Tests — passing cases
# ---------------------------------------------------------------------------


class TestValidateRegistrationsPass:
    def test_empty_registrations_passes(self) -> None:
        validate_registrations({})  # Should not raise.

    def test_concrete_singleton_passes(self) -> None:
        regs = {Concrete: _reg(Concrete)}
        validate_registrations(regs)

    def test_all_deps_registered_passes(self) -> None:
        regs = {
            Concrete: _reg(Concrete),
            NeedsConcrete: _reg(NeedsConcrete),
        }
        validate_registrations(regs)

    def test_factory_registration_skips_dep_check(self) -> None:
        # Factory-based registrations are not inspected for deps.
        regs = {
            NeedsConcrete: _reg(NeedsConcrete, factory=lambda p: NeedsConcrete(Concrete())),
        }
        validate_registrations(regs)

    def test_instance_registration_skips_checks(self) -> None:
        regs = {
            Concrete: _reg(Concrete, instance=Concrete()),
        }
        validate_registrations(regs)


# ---------------------------------------------------------------------------
# Tests — failing cases (each error type)
# ---------------------------------------------------------------------------


class TestValidateAbstractImplementation:
    def test_abstract_impl_raises(self) -> None:
        regs = {IAbstract: _reg(IAbstract)}
        with pytest.raises(StartupValidationError) as exc_info:
            validate_registrations(regs)
        assert any("abstract" in e.lower() for e in exc_info.value.errors)


class TestValidateMissingDependency:
    def test_missing_required_dep_raises(self) -> None:
        # NeedsConcrete requires Concrete, but Concrete is NOT registered.
        regs = {NeedsConcrete: _reg(NeedsConcrete)}
        with pytest.raises(StartupValidationError) as exc_info:
            validate_registrations(regs)
        assert any("Concrete" in e for e in exc_info.value.errors)

    def test_optional_dep_not_flagged(self) -> None:
        # NeedsOptional has a default for `dep`; should not be flagged.
        regs = {NeedsOptional: _reg(NeedsOptional)}
        validate_registrations(regs)  # Should not raise.


class TestValidateCircularDependency:
    def test_circular_dependency_detected(self) -> None:
        regs = {
            CycleA: _reg(CycleA),
            CycleB: _reg(CycleB),
        }
        with pytest.raises(StartupValidationError) as exc_info:
            validate_registrations(regs)
        assert any("Circular" in e for e in exc_info.value.errors)


class TestValidateLifetimeConsistency:
    def test_singleton_capturing_scoped_raises(self) -> None:
        regs = {
            ScopedDep: _reg(ScopedDep, lifetime=ServiceLifetime.SCOPED),
            SingletonCapture: _reg(SingletonCapture, lifetime=ServiceLifetime.SINGLETON),
        }
        with pytest.raises(StartupValidationError) as exc_info:
            validate_registrations(regs)
        assert any("Lifetime violation" in e for e in exc_info.value.errors)

    def test_singleton_capturing_singleton_is_fine(self) -> None:
        regs = {
            Concrete: _reg(Concrete, lifetime=ServiceLifetime.SINGLETON),
            NeedsConcrete: _reg(NeedsConcrete, lifetime=ServiceLifetime.SINGLETON),
        }
        validate_registrations(regs)  # Should not raise.


class TestMultipleErrorsCollected:
    def test_multiple_errors_in_one_exception(self) -> None:
        # Missing dep + circular dep → both should appear.
        regs = {
            NeedsConcrete: _reg(NeedsConcrete),  # Missing Concrete
            CycleA: _reg(CycleA),
            CycleB: _reg(CycleB),
        }
        with pytest.raises(StartupValidationError) as exc_info:
            validate_registrations(regs)
        assert len(exc_info.value.errors) >= 2
