"""Decorators for marking classes for automatic DI registration.

Decorating a class with ``@injectable``, ``@singleton``, ``@scoped``, or
``@transient`` attaches metadata that :class:`~.discovery.ServiceDiscovery`
reads when scanning packages.  The decorators themselves do *not* register
anything — they simply mark intent.

Example::

    from infrastructure.dependency_injection.decorators import singleton, transient
    from infrastructure.dependency_injection.lifetimes import ServiceLifetime

    @singleton(service_type=ILogger)
    class StructLogger:
        def __init__(self, config: LoggingConfig) -> None: ...

    @transient()
    class DocumentValidator:
        def __init__(self, repo: IDocumentRepository) -> None: ...
"""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from infrastructure.dependency_injection.lifetimes import ServiceLifetime

T = TypeVar("T")

# Private attribute names attached to decorated classes.
_DI_LIFETIME_ATTR = "_di_lifetime"
_DI_SERVICE_ATTR = "_di_service_type"


# ---------------------------------------------------------------------------
# Primary decorator
# ---------------------------------------------------------------------------


def injectable(
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
    service_type: type | None = None,
) -> Callable[[type[T]], type[T]]:
    """Mark a class for automatic DI registration.

    Args:
        lifetime: The :class:`~.lifetimes.ServiceLifetime` to use when the
            class is auto-registered.  Defaults to ``TRANSIENT``.
        service_type: The abstract interface/Protocol to register this class
            *as*.  When ``None``, the decorated class is registered as its
            own service type.

    Returns:
        A class decorator that attaches DI metadata without modifying the
        class behaviour.

    Example::

        @injectable(ServiceLifetime.SINGLETON, service_type=ICommandBus)
        class InMemoryCommandBus:
            def __init__(self, logger: LoggerFactory) -> None: ...
    """

    def decorator(cls: type[T]) -> type[T]:
        setattr(cls, _DI_LIFETIME_ATTR, lifetime)
        setattr(cls, _DI_SERVICE_ATTR, service_type)
        return cls

    return decorator


# ---------------------------------------------------------------------------
# Shorthand decorators
# ---------------------------------------------------------------------------


def singleton(
    service_type: type | None = None,
) -> Callable[[type[T]], type[T]]:
    """Shorthand for ``@injectable(ServiceLifetime.SINGLETON)``.

    Args:
        service_type: Optional abstract type to register as.

    Returns:
        Class decorator.

    Example::

        @singleton(service_type=IEventBus)
        class InMemoryEventBus: ...
    """
    return injectable(ServiceLifetime.SINGLETON, service_type=service_type)


def scoped(
    service_type: type | None = None,
) -> Callable[[type[T]], type[T]]:
    """Shorthand for ``@injectable(ServiceLifetime.SCOPED)``.

    Args:
        service_type: Optional abstract type to register as.

    Returns:
        Class decorator.

    Example::

        @scoped()
        class PipelineContext: ...
    """
    return injectable(ServiceLifetime.SCOPED, service_type=service_type)


def transient(
    service_type: type | None = None,
) -> Callable[[type[T]], type[T]]:
    """Shorthand for ``@injectable(ServiceLifetime.TRANSIENT)``.

    Args:
        service_type: Optional abstract type to register as.

    Returns:
        Class decorator.

    Example::

        @transient(service_type=IValidator)
        class DocumentSchemaValidator: ...
    """
    return injectable(ServiceLifetime.TRANSIENT, service_type=service_type)


# ---------------------------------------------------------------------------
# Introspection helpers
# ---------------------------------------------------------------------------


def is_injectable(cls: Any) -> bool:
    """Return ``True`` if *cls* has been decorated with ``@injectable``.

    Args:
        cls: Any object to inspect.

    Returns:
        ``bool``.
    """
    return hasattr(cls, _DI_LIFETIME_ATTR)


def get_lifetime(cls: Any) -> ServiceLifetime:
    """Return the :class:`~.lifetimes.ServiceLifetime` set on *cls*.

    Args:
        cls: A class decorated with ``@injectable`` (or a shorthand).

    Returns:
        The configured :class:`~.lifetimes.ServiceLifetime`.

    Raises:
        AttributeError: If *cls* is not injectable.
    """
    return getattr(cls, _DI_LIFETIME_ATTR)


def get_service_type(cls: type) -> type | None:
    """Return the abstract service type configured on *cls*, or ``None``.

    Args:
        cls: A class decorated with ``@injectable`` (or a shorthand).

    Returns:
        The registered-as type, or ``None`` when not set (meaning the class
        registers as itself).
    """
    return getattr(cls, _DI_SERVICE_ATTR, None)
