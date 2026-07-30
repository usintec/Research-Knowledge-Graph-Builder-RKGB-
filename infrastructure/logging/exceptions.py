"""Logging-specific exception hierarchy for RKGB.

All logging exceptions inherit from ``LoggingError`` so that callers can
catch the broadest category or a specific sub-type as needed.
"""

from __future__ import annotations

from shared.exceptions import RKGBError


class LoggingError(RKGBError):
    """Root exception for all logging framework errors."""


class LoggingNotInitialisedError(LoggingError):
    """Raised when a logger is requested before the framework is bootstrapped."""

    def __init__(self) -> None:
        super().__init__(
            "LoggingManager has not been initialised. "
            "Call bootstrap_logging() before requesting loggers.",
            code="LOGGING_NOT_INITIALISED",
        )


class LoggingConfigurationError(LoggingError):
    """Raised when the logging framework cannot be configured as requested.

    Args:
        reason: Human-readable explanation of the configuration failure.
    """

    def __init__(self, reason: str) -> None:
        super().__init__(
            f"Logging configuration error: {reason}",
            code="LOGGING_CONFIGURATION_ERROR",
        )
        self.reason = reason


class HandlerRegistrationError(LoggingError):
    """Raised when a handler cannot be registered.

    Args:
        handler_id: Identifier of the handler that failed.
        reason: Human-readable explanation.
    """

    def __init__(self, handler_id: str, reason: str) -> None:
        super().__init__(
            f"Failed to register log handler '{handler_id}': {reason}",
            code="HANDLER_REGISTRATION_ERROR",
        )
        self.handler_id = handler_id
        self.reason = reason


class FormatterNotFoundError(LoggingError):
    """Raised when a requested formatter is not available.

    Args:
        format_id: The requested format identifier.
    """

    def __init__(self, format_id: str) -> None:
        super().__init__(
            f"Log formatter '{format_id}' is not registered.",
            code="FORMATTER_NOT_FOUND",
        )
        self.format_id = format_id
