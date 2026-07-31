"""Bootstrap helper for the RKGB Dependency Injection container.

Provides the single entry-point function :func:`bootstrap_container` that
wires configuration, logging, and all registration modules into a ready-to-use
:class:`~.service_provider.ServiceProvider`.

Call this once during application startup, after
:func:`~infrastructure.config.bootstrap.bootstrap_config` and
:func:`~infrastructure.logging.bootstrap.bootstrap_logging` have completed.

Typical startup sequence::

    from infrastructure.config.bootstrap import bootstrap_config
    from infrastructure.logging.bootstrap import bootstrap_logging
    from infrastructure.dependency_injection.bootstrap import bootstrap_container

    config  = bootstrap_config()
    logging = bootstrap_logging(config)
    provider = bootstrap_container(config, logging)

    # From here, resolve services through the provider:
    factory = provider.resolve(LoggerFactory)
    logger  = factory.get_logger("app")

DI container integration in ``app/main.py``::

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        config_manager  = bootstrap_config()
        logging_manager = bootstrap_logging(config_manager)
        service_provider = bootstrap_container(config_manager, logging_manager)
        # ... yield ...
        # Cleanup (if needed) goes here.
"""

from __future__ import annotations

from infrastructure.config.manager import ConfigManager
from infrastructure.dependency_injection.composition_root import CompositionRoot
from infrastructure.dependency_injection.service_provider import ServiceProvider
from infrastructure.logging.manager import LoggingManager


def bootstrap_container(
    config_manager: ConfigManager,
    logging_manager: LoggingManager,
    extra_modules: list[object] | None = None,
    *,
    skip_validation: bool = False,
) -> ServiceProvider:
    """Assemble and return the root :class:`~.service_provider.ServiceProvider`.

    This is the canonical entry point for DI container construction.

    Args:
        config_manager: A fully loaded
            :class:`~infrastructure.config.manager.ConfigManager` produced by
            :func:`~infrastructure.config.bootstrap.bootstrap_config`.
        logging_manager: An initialised
            :class:`~infrastructure.logging.manager.LoggingManager` produced by
            :func:`~infrastructure.logging.bootstrap.bootstrap_logging`.
        extra_modules: Optional list of additional registration modules applied
            after the standard platform modules.  Use for feature-specific
            services, plugin registrations, or application-layer bindings.
        skip_validation: When ``True``, startup validation is skipped.
            Intended only for unit tests building partial containers.

    Returns:
        Fully configured root :class:`~.service_provider.ServiceProvider`.

    Raises:
        :class:`~.exceptions.StartupValidationError`: If validation finds
            problems in the registrations and ``skip_validation`` is ``False``.

    Example::

        provider = bootstrap_container(config_manager, logging_manager)
        factory  = provider.resolve(LoggerFactory)
    """
    root = CompositionRoot(
        config_manager=config_manager,
        logging_manager=logging_manager,
        extra_modules=extra_modules,
        skip_validation=skip_validation,
    )
    return root.build()


def build_test_container(
    config_manager: ConfigManager | None = None,
    logging_manager: LoggingManager | None = None,
    extra_modules: list[object] | None = None,
) -> ServiceProvider:
    """Build a hermetic DI container suitable for unit tests.

    No external services are required.  Config and logging are initialised
    with safe in-memory defaults when not supplied.

    Args:
        config_manager: Optional pre-built
            :class:`~infrastructure.config.manager.ConfigManager`.
            When ``None``, a minimal test config is built automatically.
        logging_manager: Optional pre-built
            :class:`~infrastructure.logging.manager.LoggingManager`.
            When ``None``, a test logging manager is built automatically.
        extra_modules: Optional additional registration modules.

    Returns:
        Configured :class:`~.service_provider.ServiceProvider` with startup
        validation disabled.

    Example::

        from infrastructure.dependency_injection.bootstrap import build_test_container

        provider = build_test_container()
        factory  = provider.resolve(LoggerFactory)
        logger   = factory.get_logger("test")
    """
    if config_manager is None:
        from infrastructure.config.environment import Environment
        from infrastructure.config.providers.yaml_provider import RuntimeOverrideProvider

        config_manager = ConfigManager(
            providers=[
                RuntimeOverrideProvider(overrides={"application": {"env": "testing"}})
            ],
            env=Environment.TESTING,
        )
        config_manager.load()

    if logging_manager is None:
        from infrastructure.logging.bootstrap import build_test_logging_manager

        logging_manager = build_test_logging_manager()

    return bootstrap_container(
        config_manager,
        logging_manager,
        extra_modules=extra_modules,
        skip_validation=True,
    )
