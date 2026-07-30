"""Configuration-specific exception hierarchy for RKGB.

All configuration exceptions inherit from ``ConfigError`` so that callers
can catch the broadest category or a specific sub-type as needed.
"""

from __future__ import annotations

from shared.exceptions import RKGBError


class ConfigError(RKGBError):
    """Root exception for all configuration framework errors."""


class ConfigLoadError(ConfigError):
    """Raised when a configuration source cannot be read or parsed.

    Args:
        source: The file path, URL, or provider name that failed.
        reason: Human-readable explanation.
    """

    def __init__(self, source: str, reason: str) -> None:
        super().__init__(
            f"Failed to load configuration from '{source}': {reason}",
            code="CONFIG_LOAD_ERROR",
        )
        self.source = source
        self.reason = reason


class ConfigValidationError(ConfigError):
    """Raised when a configuration section fails validation.

    Args:
        section: The configuration section name.
        details: Validation error details (Pydantic error string or similar).
    """

    def __init__(self, section: str, details: str) -> None:
        super().__init__(
            f"Configuration validation failed for section '{section}': {details}",
            code="CONFIG_VALIDATION_ERROR",
        )
        self.section = section
        self.details = details


class ConfigProviderError(ConfigError):
    """Raised when a configuration provider fails during ``load()``.

    Args:
        provider: The provider name.
        reason: Human-readable explanation.
    """

    def __init__(self, provider: str, reason: str) -> None:
        super().__init__(
            f"Configuration provider '{provider}' encountered an error: {reason}",
            code="CONFIG_PROVIDER_ERROR",
        )
        self.provider = provider
        self.reason = reason


class ConfigSectionNotFoundError(ConfigError):
    """Raised when a requested configuration section is not registered.

    Args:
        key: The registry key that was not found.
    """

    def __init__(self, key: str) -> None:
        super().__init__(
            f"Configuration section '{key}' is not registered.",
            code="CONFIG_SECTION_NOT_FOUND",
        )
        self.key = key


class ConfigNotInitialisedError(ConfigError):
    """Raised when configuration is accessed before the manager is bootstrapped."""

    def __init__(self) -> None:
        super().__init__(
            "ConfigManager has not been initialised. "
            "Call bootstrap_config() before accessing configuration.",
            code="CONFIG_NOT_INITIALISED",
        )


class ConfigEnvironmentError(ConfigError):
    """Raised when an invalid or unsupported environment is specified.

    Args:
        env_value: The unrecognised environment string.
    """

    def __init__(self, env_value: str) -> None:
        super().__init__(
            f"Unrecognised environment value: '{env_value}'. "
            "Set APP_ENV to one of: local, development, testing, staging, production, docker, ci.",
            code="CONFIG_ENVIRONMENT_ERROR",
        )
        self.env_value = env_value
