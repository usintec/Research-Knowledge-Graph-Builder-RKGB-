"""RKGB Logging & Observability Framework.

This package provides the centralised logging infrastructure for the entire
RKGB platform.  It is the foundation of the observability strategy and is
designed to support:

* Structured logging (JSON for production, human-readable for development)
* Correlation context propagation via ``contextvars``
* Dependency-injection-friendly logger creation
* Future OpenTelemetry, Prometheus, and distributed tracing integration

**Public API** — import from here, not from sub-modules::

    from infrastructure.logging import (
        bootstrap_logging,
        build_test_logging_manager,
        LoggingManager,
        LoggerFactory,
        RKGBLogger,
        ILogger,
        CorrelationContext,
        LogEntry,
        ExceptionInfo,
        generate_correlation_id,
        generate_trace_id,
        set_correlation_context,
        get_correlation_context,
        clear_correlation_context,
        reset_correlation_context,
    )

Do **not** import ``structlog``, ``logging``, or any sub-module from business
code.  Always obtain loggers via :class:`LoggerFactory`.
"""

from __future__ import annotations

from infrastructure.logging.bootstrap import bootstrap_logging, build_test_logging_manager
from infrastructure.logging.context import (
    clear_correlation_context,
    get_correlation_context,
    reset_correlation_context,
    set_correlation_context,
)
from infrastructure.logging.correlation import generate_correlation_id, generate_trace_id
from infrastructure.logging.exceptions import (
    FormatterNotFoundError,
    HandlerRegistrationError,
    LoggingConfigurationError,
    LoggingError,
    LoggingNotInitialisedError,
)
from infrastructure.logging.factory import LoggerFactory
from infrastructure.logging.interfaces import ICorrelationProvider, ILogger, IMetricsEmitter
from infrastructure.logging.logger import RKGBLogger
from infrastructure.logging.manager import LoggingManager
from infrastructure.logging.models import CorrelationContext, LogEntry
from infrastructure.logging.models.log_entry import ExceptionInfo

__all__ = [
    # Bootstrap
    "bootstrap_logging",
    "build_test_logging_manager",
    # Manager & Factory
    "LoggingManager",
    "LoggerFactory",
    # Logger
    "RKGBLogger",
    # Interfaces
    "ILogger",
    "ICorrelationProvider",
    "IMetricsEmitter",
    # Models
    "CorrelationContext",
    "LogEntry",
    "ExceptionInfo",
    # Context management
    "set_correlation_context",
    "get_correlation_context",
    "reset_correlation_context",
    "clear_correlation_context",
    # Correlation ID generation
    "generate_correlation_id",
    "generate_trace_id",
    # Exceptions
    "LoggingError",
    "LoggingNotInitialisedError",
    "LoggingConfigurationError",
    "HandlerRegistrationError",
    "FormatterNotFoundError",
]
