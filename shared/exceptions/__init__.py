"""Base exception hierarchy for RKGB.

All application-level exceptions should inherit from ``RKGBError``
so that callers can catch the broadest category when needed.
"""

from __future__ import annotations


class RKGBError(Exception):
    """Root exception for all RKGB application errors."""

    def __init__(self, message: str, *, code: str | None = None) -> None:
        """Initialise the exception.

        Args:
            message: Human-readable error description.
            code: Optional machine-readable error code.
        """
        super().__init__(message)
        self.message = message
        self.code = code

    def __repr__(self) -> str:  # noqa: D105
        return f"{type(self).__name__}(message={self.message!r}, code={self.code!r})"


class ConfigurationError(RKGBError):
    """Raised when the application is misconfigured."""


class NotFoundError(RKGBError):
    """Raised when a requested resource cannot be located."""


class ValidationError(RKGBError):
    """Raised when input data fails validation rules."""


class DuplicateError(RKGBError):
    """Raised when an entity already exists and uniqueness is required."""


class AuthorisationError(RKGBError):
    """Raised when an operation is not permitted for the requesting actor."""
