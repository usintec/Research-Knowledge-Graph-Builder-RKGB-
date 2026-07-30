"""Logger Factory for the RKGB Logging & Observability Framework.

:class:`LoggerFactory` is the sole entry point for obtaining logger instances.
Business code should never call ``structlog.get_logger()`` or
``logging.getLogger()`` directly — always obtain a logger via the factory
injected through the DI container.

Usage::

    # Wired up by the DI container (Step A4):
    factory: LoggerFactory = container.resolve(LoggerFactory)
    logger = factory.get_logger("my_service")
    logger.info("service_started")

    # With additional bound context:
    scoped = factory.get_logger("pipeline.ingestion", pipeline_id="pipe-001")
    scoped.debug("reading_document", doc_id="doc-xyz")
"""

from __future__ import annotations

from typing import Any

import structlog

from infrastructure.logging.logger import RKGBLogger


class LoggerFactory:
    """Factory that creates component-specific :class:`~infrastructure.logging.logger.RKGBLogger` instances.

    Each logger is bound with the component name and any additional context
    provided at creation time.  The factory delegates actual logger retrieval
    to structlog, ensuring the global processor chain is always applied.

    :class:`LoggerFactory` is designed to be singleton-scoped in the DI
    container — one factory serves the entire application.

    Args:
        default_extra: Optional key-value pairs bound to every logger this
            factory creates.  Useful for application-level context such as
            ``app_version`` or ``deployment_region``.
    """

    def __init__(self, default_extra: dict[str, Any] | None = None) -> None:
        self._default_extra: dict[str, Any] = default_extra or {}

    def get_logger(self, component: str, **context: Any) -> RKGBLogger:  # noqa: ANN401
        """Return a structured logger bound to a specific component.

        The returned logger carries:
        * The component name in every log entry.
        * Any ``default_extra`` fields set on the factory.
        * Any ``context`` fields passed to this call.

        Args:
            component: Logical component name (e.g. ``"pipeline.ingestion"``,
                ``"command_bus"``, ``"neo4j_repository"``).
            **context: Additional key-value fields bound to this logger instance.

        Returns:
            :class:`~infrastructure.logging.logger.RKGBLogger` ready for use.
        """
        bound = structlog.get_logger(component)

        if self._default_extra:
            bound = bound.bind(**self._default_extra)

        if context:
            bound = bound.bind(**context)

        return RKGBLogger(bound_logger=bound, component=component)

    def with_extra(self, **extra: Any) -> "LoggerFactory":  # noqa: ANN401
        """Return a new factory with additional default context fields.

        The original factory is not modified.

        Args:
            **extra: Key-value pairs to add to every logger this new factory
                creates.

        Returns:
            New :class:`LoggerFactory` with merged defaults.
        """
        merged = {**self._default_extra, **extra}
        return LoggerFactory(default_extra=merged)
