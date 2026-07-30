"""Log filters for the RKGB Logging & Observability Framework.

Filters operate as structlog processors — they sit in the processor chain
and can suppress, enrich, or transform log records before they reach a handler.

Implemented filters:
    * :class:`LogLevelFilter` — drops entries below a minimum level
    * :class:`CorrelationContextFilter` — merges active context-var fields
    * :class:`ThirdPartySuppressionFilter` — raises log levels for noisy libs
    * :class:`SensitiveDataFilter` — redacts fields that should never appear
"""

from __future__ import annotations

import logging
from typing import Any

import structlog

from infrastructure.logging.constants import THIRD_PARTY_LOGGERS
from infrastructure.logging.interfaces import ILogFilter

_LOG_LEVEL_ORDER: dict[str, int] = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


class LogLevelFilter(ILogFilter):
    """Drop log records below a configured minimum level.

    Useful when a specific logger should have a higher threshold than the
    global minimum set on the root logger.

    Args:
        min_level: Minimum log level to pass through (e.g. ``"warning"``).
    """

    def __init__(self, min_level: str) -> None:
        self._min_level = min_level.lower()
        self._min_numeric = _LOG_LEVEL_ORDER.get(self._min_level, logging.DEBUG)

    def __call__(
        self,
        logger: Any,  # noqa: ANN401
        method: str,
        event_dict: dict[str, Any],  # noqa: ANN401
    ) -> dict[str, Any]:  # noqa: ANN401
        """Drop the event if its level is below the minimum.

        Args:
            logger: Bound structlog logger.
            method: Log level method name.
            event_dict: Mutable event dictionary.

        Returns:
            Unchanged ``event_dict`` if the level passes.

        Raises:
            :exc:`structlog.DropEvent`: If the level is below the minimum.
        """
        numeric = _LOG_LEVEL_ORDER.get(method.lower(), logging.DEBUG)
        if numeric < self._min_numeric:
            raise structlog.DropEvent()
        return event_dict


class CorrelationContextFilter(ILogFilter):
    """Merge any context-var fields not already present in the event dict.

    structlog's ``merge_contextvars`` processor handles this automatically
    when using the stdlib integration.  This filter provides an explicit
    fallback for pipeline or background-worker paths that bypass stdlib.
    """

    def __call__(
        self,
        logger: Any,  # noqa: ANN401
        method: str,
        event_dict: dict[str, Any],  # noqa: ANN401
    ) -> dict[str, Any]:  # noqa: ANN401
        """Merge active correlation context into the event dict.

        Args:
            logger: Bound structlog logger.
            method: Log level method name.
            event_dict: Mutable event dictionary.

        Returns:
            ``event_dict`` enriched with active context fields.
        """
        from infrastructure.logging.context import get_correlation_context

        ctx = get_correlation_context()
        if ctx is not None:
            ctx_dict = ctx.to_log_dict()
            for key, value in ctx_dict.items():
                if key not in event_dict:
                    event_dict[key] = value
        return event_dict


class ThirdPartySuppressionFilter(ILogFilter):
    """Raise the effective log level for known noisy third-party loggers.

    When ``LoggingConfig.suppress_third_party`` is ``True``, this filter
    drops DEBUG and INFO records produced by loggers whose names match the
    :data:`~infrastructure.logging.constants.THIRD_PARTY_LOGGERS` list.

    Args:
        suppressed_loggers: Tuple of logger name prefixes to suppress.
            Defaults to :data:`THIRD_PARTY_LOGGERS`.
    """

    def __init__(
        self,
        suppressed_loggers: tuple[str, ...] = THIRD_PARTY_LOGGERS,
    ) -> None:
        self._suppressed = suppressed_loggers

    def __call__(
        self,
        logger: Any,  # noqa: ANN401
        method: str,
        event_dict: dict[str, Any],  # noqa: ANN401
    ) -> dict[str, Any]:  # noqa: ANN401
        """Drop DEBUG/INFO records from suppressed loggers.

        Args:
            logger: Bound structlog logger.
            method: Log level method name.
            event_dict: Mutable event dictionary.

        Returns:
            Unchanged ``event_dict`` if the record should pass.

        Raises:
            :exc:`structlog.DropEvent`: For suppressed low-level entries.
        """
        logger_name: str = event_dict.get("logger", "")
        if any(logger_name.startswith(prefix) for prefix in self._suppressed):
            if method.lower() in ("debug", "info"):
                raise structlog.DropEvent()
        return event_dict


class SensitiveDataFilter(ILogFilter):
    """Redact field values that must never appear in logs.

    Replaces the value of any key matching the redaction list with
    ``"[REDACTED]"``.  Defaults cover the most common credential fields.

    Args:
        redact_keys: Set of exact field names to redact.
    """

    _DEFAULT_KEYS: frozenset[str] = frozenset({
        "password",
        "secret",
        "token",
        "api_key",
        "access_token",
        "refresh_token",
        "authorization",
        "private_key",
        "client_secret",
        "neo4j_password",
    })

    def __init__(self, redact_keys: frozenset[str] | None = None) -> None:
        self._redact_keys = redact_keys or self._DEFAULT_KEYS

    def __call__(
        self,
        logger: Any,  # noqa: ANN401
        method: str,
        event_dict: dict[str, Any],  # noqa: ANN401
    ) -> dict[str, Any]:  # noqa: ANN401
        """Redact sensitive fields in the event dict.

        Args:
            logger: Bound structlog logger.
            method: Log level method name.
            event_dict: Mutable event dictionary.

        Returns:
            ``event_dict`` with sensitive values replaced by ``"[REDACTED]"``.
        """
        for key in self._redact_keys:
            if key in event_dict:
                event_dict[key] = "[REDACTED]"
        return event_dict
