"""Exceptions for the RKGB Dependency Injection Framework.

All exceptions derive from :class:`DIError` so callers can catch the entire
DI error family with a single ``except DIError`` clause if needed.
"""

from __future__ import annotations


class DIError(Exception):
    """Base exception for all DI framework errors."""


class ServiceNotFoundError(DIError):
    """Raised when a requested service type has no registration.

    Args:
        service_type: The type that could not be resolved.
    """

    def __init__(self, service_type: type) -> None:
        self.service_type = service_type
        super().__init__(
            f"No service registered for type '{service_type.__qualname__}'. "
            "Register it via ServiceCollection before attempting resolution."
        )


class CircularDependencyError(DIError):
    """Raised when a circular dependency chain is detected during resolution.

    Args:
        chain: Ordered list of types forming the cycle, ending with the
            type that re-appeared.
    """

    def __init__(self, chain: list[type]) -> None:
        self.chain = chain
        names = " → ".join(t.__qualname__ for t in chain)
        super().__init__(f"Circular dependency detected: {names}")


class DuplicateRegistrationError(DIError):
    """Raised when the same service type is registered more than once.

    Pass ``replace=True`` to the registration method to intentionally
    override an existing registration.

    Args:
        service_type: The type that was registered a second time.
    """

    def __init__(self, service_type: type) -> None:
        self.service_type = service_type
        super().__init__(
            f"Service '{service_type.__qualname__}' is already registered. "
            "Pass replace=True to override an existing registration."
        )


class InvalidLifetimeError(DIError):
    """Raised when a service lifetime configuration is invalid.

    Args:
        message: Description of the invalid lifetime configuration.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ServiceResolutionError(DIError):
    """Raised when a service cannot be constructed.

    Wraps the underlying exception to provide context about which service
    failed and why.

    Args:
        service_type: The type whose construction failed.
        reason: Human-readable description of the failure.
    """

    def __init__(self, service_type: type, reason: str) -> None:
        self.service_type = service_type
        super().__init__(
            f"Failed to resolve '{service_type.__qualname__}': {reason}"
        )


class ScopeError(DIError):
    """Raised on invalid scope operations.

    Common causes:
    * Resolving a scoped service from the root provider (outside any scope).
    * Accessing scope state after the scope has been disposed.

    Args:
        message: Description of the scope violation.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class StartupValidationError(DIError):
    """Raised when startup validation finds problems in the registrations.

    The application should fail fast at startup rather than encountering
    resolution errors at runtime.

    Args:
        errors: List of individual validation error messages.
    """

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        formatted = "\n  - ".join(errors)
        super().__init__(
            f"DI container startup validation failed with {len(errors)} "
            f"error(s):\n  - {formatted}"
        )


class MissingDependencyError(DIError):
    """Raised when a required constructor dependency has no registration.

    Args:
        dependent: The type that requires the missing dependency.
        dependency: The type that is missing from the registrations.
    """

    def __init__(self, dependent: type, dependency: type) -> None:
        self.dependent = dependent
        self.dependency = dependency
        super().__init__(
            f"'{dependent.__qualname__}' requires '{dependency.__qualname__}', "
            "but it is not registered in the DI container."
        )
