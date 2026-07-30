"""Logging bootstrap module for the RKGB platform.

This module is the single call site for assembling and initialising the
``LoggingManager`` from the ``ConfigManager`` produced by Step A2.

**Call ``bootstrap_logging()`` once at startup**, immediately after
``bootstrap_config()``, inside the FastAPI lifespan handler or the CLI
entrypoint.

Bootstrap sequence:
    1. Retrieve :class:`~infrastructure.config.models.logging.LoggingConfig`
       from the :class:`~infrastructure.config.manager.ConfigManager`.
    2. Construct :class:`~infrastructure.logging.manager.LoggingManager`.
    3. Call ``manager.initialise()`` — configure structlog + stdlib handlers.
    4. Return the manager for registration with the DI container (Step A4).

DI container integration (preview — implemented in Step A4)::

    config_manager = bootstrap_config()
    logging_manager = bootstrap_logging(config_manager)

    container.define(LoggingManager, lambda: logging_manager)
    container.define(LoggerFactory, lambda: logging_manager.factory)

Integration with ``app/main.py``::

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        config_manager = bootstrap_config()
        logging_manager = bootstrap_logging(config_manager)
        try:
            yield
        finally:
            logging_manager.shutdown()
"""

from __future__ import annotations

from infrastructure.config.manager import ConfigManager
from infrastructure.config.models.logging import LoggingConfig
from infrastructure.logging.manager import LoggingManager


def bootstrap_logging(config_manager: ConfigManager) -> LoggingManager:
    """Assemble and initialise the ``LoggingManager``.

    Retrieves the :class:`~infrastructure.config.models.logging.LoggingConfig`
    from the supplied manager, builds a :class:`LoggingManager`, and calls
    ``initialise()`` so logging is ready before any other component starts.

    Args:
        config_manager: A fully loaded
            :class:`~infrastructure.config.manager.ConfigManager` (i.e.
            ``bootstrap_config()`` has already been called).

    Returns:
        Initialised :class:`~infrastructure.logging.manager.LoggingManager`.

    Example::

        from infrastructure.config.bootstrap import bootstrap_config
        from infrastructure.logging.bootstrap import bootstrap_logging

        config_manager = bootstrap_config()
        logging_manager = bootstrap_logging(config_manager)
        logger = logging_manager.factory.get_logger("my_service")
        logger.info("service_started")
    """
    logging_config: LoggingConfig = config_manager.get(LoggingConfig)
    manager = LoggingManager(config=logging_config)
    manager.initialise()
    return manager


def build_test_logging_manager(
    overrides: dict[str, object] | None = None,
) -> LoggingManager:
    """Build a ``LoggingManager`` suitable for unit tests.

    Uses a minimal hermetic configuration (no file I/O, DEBUG level,
    console format) so tests are fast and produce readable output.

    Args:
        overrides: Optional dict of
            :class:`~infrastructure.config.models.logging.LoggingConfig`
            field overrides.

    Returns:
        Initialised :class:`~infrastructure.logging.manager.LoggingManager`.

    Example::

        manager = build_test_logging_manager({"level": "WARNING"})
        logger = manager.factory.get_logger("test_component")
        logger.warning("test_warning_emitted")
    """
    from infrastructure.config.models.logging import LogFileConfig, LogFormat, LogLevel

    defaults: dict[str, object] = {
        "level": LogLevel.DEBUG,
        "format": LogFormat.CONSOLE,
        "include_timestamp": False,
        "include_caller": False,
        "suppress_third_party": False,
        "file": LogFileConfig(enabled=False),
    }
    if overrides:
        defaults.update(overrides)

    config = LoggingConfig(**defaults)  # type: ignore[arg-type]
    manager = LoggingManager(config=config)
    manager.initialise()
    return manager
