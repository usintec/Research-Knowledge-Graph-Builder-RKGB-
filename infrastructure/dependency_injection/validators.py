"""Startup validators for the RKGB Dependency Injection Framework.

Validates the full registration map before the application starts accepting
requests.  The goal is *fail fast* — surface configuration problems at boot
time rather than at the moment a service is first resolved in production.

Checks performed:
    1. All concrete implementation types are instantiable (not abstract).
    2. Every required constructor dependency is registered.
    3. No circular dependency chains exist.
    4. Singleton services do not capture scoped services (lifetime leaks).
"""

from __future__ import annotations

import inspect
import typing

from infrastructure.dependency_injection.exceptions import StartupValidationError
from infrastructure.dependency_injection.lifetimes import ServiceLifetime
from infrastructure.dependency_injection.registration import ServiceRegistration


def validate_registrations(registrations: dict[type, ServiceRegistration]) -> None:
    """Run all startup validations against *registrations*.

    Collects every error found (rather than stopping at the first) so the
    developer sees the full picture in one shot.

    Args:
        registrations: Complete map of service type →
            :class:`~.registration.ServiceRegistration` produced by the
            :class:`~.service_collection.ServiceCollection`.

    Raises:
        StartupValidationError: When one or more validation checks fail.
            The exception message lists every individual error.
    """
    errors: list[str] = []
    errors.extend(_validate_implementations_are_concrete(registrations))
    errors.extend(_validate_dependencies_are_registered(registrations))
    errors.extend(_validate_no_circular_dependencies(registrations))
    errors.extend(_validate_lifetime_consistency(registrations))

    if errors:
        raise StartupValidationError(errors)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _resolve_hints(fn: object) -> dict[str, Any]:
    """Return fully-resolved type hints for *fn*, handling string annotations.

    Falls back to an empty dict when resolution fails (e.g. unresolvable
    forward references) so callers can degrade gracefully.

    Args:
        fn: A callable whose ``__annotations__`` should be resolved.

    Returns:
        Dict mapping parameter name → resolved type.
    """
    try:
        return typing.get_type_hints(fn)
    except Exception:
        return {}


def _validate_implementations_are_concrete(
    registrations: dict[type, ServiceRegistration],
) -> list[str]:
    """Check that every concrete type targeted for construction is not abstract.

    Factory- and instance-based registrations are excluded — those bypass
    constructor injection entirely.

    Args:
        registrations: The registration map to validate.

    Returns:
        List of error strings (empty when all checks pass).
    """
    errors: list[str] = []
    for service_type, reg in registrations.items():
        if reg.instance is not None or reg.factory is not None:
            continue  # Not constructed via reflection; skip.

        concrete = reg.concrete_type
        if inspect.isabstract(concrete):
            errors.append(
                f"'{service_type.__qualname__}' maps to abstract type "
                f"'{concrete.__qualname__}'. Provide a concrete implementation."
            )
    return errors


def _validate_dependencies_are_registered(
    registrations: dict[type, ServiceRegistration],
) -> list[str]:
    """Check that every required constructor parameter has a registration.

    Parameters with defaults are optional — they are skipped even when not
    registered (the constructor default will be used at runtime).

    Uses :func:`typing.get_type_hints` to resolve string annotations produced
    by ``from __future__ import annotations`` (PEP 563).

    Args:
        registrations: The registration map to validate.

    Returns:
        List of error strings (empty when all checks pass).
    """
    errors: list[str] = []
    for service_type, reg in registrations.items():
        if reg.instance is not None or reg.factory is not None:
            continue

        concrete = reg.concrete_type
        try:
            sig = inspect.signature(concrete.__init__)
        except (ValueError, TypeError):
            continue  # Cannot inspect; skip — runtime will surface the error.

        hints = _resolve_hints(concrete.__init__)

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            annotation = hints.get(param_name, param.annotation)
            if annotation is inspect.Parameter.empty:
                continue  # No type hint; skip.

            has_default = param.default is not inspect.Parameter.empty
            if annotation not in registrations and not has_default:
                type_name = (
                    annotation.__qualname__
                    if hasattr(annotation, "__qualname__")
                    else repr(annotation)
                )
                errors.append(
                    f"'{service_type.__qualname__}' requires '{type_name}' "
                    f"(parameter '{param_name}'), which is not registered."
                )
    return errors


def _validate_no_circular_dependencies(
    registrations: dict[type, ServiceRegistration],
) -> list[str]:
    """Detect circular dependency chains using iterative DFS.

    Uses :func:`typing.get_type_hints` to resolve string annotations.

    Args:
        registrations: The registration map to validate.

    Returns:
        List of error strings describing each detected cycle.
    """
    errors: list[str] = []
    visited: set[type] = set()

    def _direct_deps(reg: ServiceRegistration) -> list[type]:
        """Return typed constructor dependencies for *reg* that are registered."""
        if reg.instance is not None or reg.factory is not None:
            return []
        try:
            sig = inspect.signature(reg.concrete_type.__init__)
        except (ValueError, TypeError):
            return []
        hints = _resolve_hints(reg.concrete_type.__init__)
        return [
            hints.get(name, param.annotation)
            for name, param in sig.parameters.items()
            if name != "self"
            and hints.get(name, param.annotation) is not inspect.Parameter.empty
            and hints.get(name, param.annotation) in registrations
        ]

    def _visit(node: type, path: list[type]) -> None:
        """DFS visit, collecting cycles into *errors*."""
        if node in path:
            idx = path.index(node)
            cycle = path[idx:] + [node]
            names = " → ".join(t.__qualname__ for t in cycle)
            errors.append(f"Circular dependency detected: {names}")
            return
        if node in visited:
            return

        path.append(node)
        for dep in _direct_deps(registrations[node]):
            _visit(dep, path)
        path.pop()
        visited.add(node)

    for svc_type in list(registrations.keys()):
        if svc_type not in visited:
            _visit(svc_type, [])

    return errors


def _validate_lifetime_consistency(
    registrations: dict[type, ServiceRegistration],
) -> list[str]:
    """Detect singleton-captures-scoped lifetime violations.

    A singleton that directly depends on a scoped service will hold a
    reference to the scoped instance for the entire application lifetime,
    preventing it from being properly disposed at scope boundaries.

    Only direct (one-level) constructor dependencies are checked here.
    Uses :func:`typing.get_type_hints` to resolve string annotations.

    Args:
        registrations: The registration map to validate.

    Returns:
        List of error strings (empty when all checks pass).
    """
    errors: list[str] = []
    for service_type, reg in registrations.items():
        if reg.lifetime is not ServiceLifetime.SINGLETON:
            continue
        if reg.instance is not None or reg.factory is not None:
            continue  # Cannot inspect factory/instance deps statically.

        try:
            sig = inspect.signature(reg.concrete_type.__init__)
        except (ValueError, TypeError):
            continue

        hints = _resolve_hints(reg.concrete_type.__init__)

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            annotation = hints.get(param_name, param.annotation)
            if annotation is inspect.Parameter.empty or annotation not in registrations:
                continue

            dep_reg = registrations[annotation]
            if dep_reg.lifetime is ServiceLifetime.SCOPED:
                errors.append(
                    f"Lifetime violation: singleton '{service_type.__qualname__}' "
                    f"depends on scoped '{annotation.__qualname__}' "
                    f"(parameter '{param_name}'). "
                    "Singletons must not capture scoped services."
                )
    return errors
