"""Domain exception hierarchy.

Domain exceptions express business rule violations and should be
raised by aggregates, domain services, and specifications.
They must not reference infrastructure or application concerns.
"""

from __future__ import annotations

from shared.exceptions import RKGBError


class DomainError(RKGBError):
    """Root exception for all domain layer errors."""


class AggregateNotFoundError(DomainError):
    """Raised when an aggregate cannot be located by its identity."""


class BusinessRuleViolationError(DomainError):
    """Raised when an operation would violate a domain invariant."""


class ConcurrencyError(DomainError):
    """Raised when an optimistic concurrency conflict is detected."""
