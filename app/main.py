"""Application entry point.

This module bootstraps the RKGB platform.

Step A2 adds configuration system integration.  The ConfigManager is
bootstrapped during the FastAPI lifespan so all infrastructure components
receive their configuration via the DI container.

Step A3 adds the Logging & Observability Framework.  The LoggingManager is
bootstrapped immediately after config so every subsequent component has access
to structured, correlated logging.

Step A4 adds the Dependency Injection Framework.  The DIContainer is built
during the FastAPI lifespan after config and logging are initialised.  All
infrastructure components receive their dependencies through the container's
ServiceProvider.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from infrastructure.config.bootstrap import bootstrap_config
from infrastructure.config.manager import ConfigManager
from infrastructure.dependency_injection.bootstrap import bootstrap_container
from infrastructure.dependency_injection.service_provider import ServiceProvider
from infrastructure.logging.bootstrap import bootstrap_logging
from infrastructure.logging.manager import LoggingManager

# Module-level references — populated during lifespan.
_config_manager: ConfigManager | None = None
_logging_manager: LoggingManager | None = None
_service_provider: ServiceProvider | None = None


def get_config_manager() -> ConfigManager:
    """Return the active ConfigManager instance.

    Raises:
        RuntimeError: If called before the application has started.

    Returns:
        The bootstrapped :class:`~infrastructure.config.manager.ConfigManager`.
    """
    if _config_manager is None:
        raise RuntimeError(
            "ConfigManager is not initialised. "
            "Ensure the FastAPI lifespan has started before accessing config."
        )
    return _config_manager


def get_logging_manager() -> LoggingManager:
    """Return the active LoggingManager instance.

    Raises:
        RuntimeError: If called before the application has started.

    Returns:
        The bootstrapped :class:`~infrastructure.logging.manager.LoggingManager`.
    """
    if _logging_manager is None:
        raise RuntimeError(
            "LoggingManager is not initialised. "
            "Ensure the FastAPI lifespan has started before accessing logging."
        )
    return _logging_manager


def get_service_provider() -> ServiceProvider:
    """Return the active root ServiceProvider.

    Raises:
        RuntimeError: If called before the application has started.

    Returns:
        The bootstrapped :class:`~infrastructure.dependency_injection.service_provider.ServiceProvider`.
    """
    if _service_provider is None:
        raise RuntimeError(
            "ServiceProvider is not initialised. "
            "Ensure the FastAPI lifespan has started before resolving services."
        )
    return _service_provider


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """FastAPI lifespan — bootstraps and tears down application resources.

    Bootstrap order:
        1. ConfigManager     — loads and validates all configuration.
        2. LoggingManager    — configures structlog + stdlib from LoggingConfig.
        3. ServiceProvider   — wires all infrastructure singletons via the DI
                               container (Step A4).

    Args:
        app: The FastAPI application instance.

    Yields:
        Control to the running application.
    """
    global _config_manager, _logging_manager, _service_provider  # noqa: PLW0603

    # 1. Configuration (Step A2)
    _config_manager = bootstrap_config()
    root = _config_manager.root

    # Update the FastAPI app metadata from config (in case it differs from defaults)
    app.title = root.application.title
    app.version = root.application.version
    app.description = root.application.description

    # 2. Logging (Step A3)
    _logging_manager = bootstrap_logging(_config_manager)

    # 3. Dependency Injection (Step A4)
    _service_provider = bootstrap_container(_config_manager, _logging_manager)

    yield

    # --- Shutdown (reverse order) ---
    _service_provider = None

    if _logging_manager is not None:
        _logging_manager.shutdown()
        _logging_manager = None

    _config_manager = None


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance.

    Returns:
        Configured FastAPI application.
    """
    application = FastAPI(
        title="Research Knowledge Graph Builder",
        description=(
            "Enterprise AI platform for scientific knowledge extraction, "
            "semantic graph construction, and GraphRAG-powered research intelligence."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    @application.get("/health", tags=["System"])
    async def health_check() -> dict[str, str]:
        """Liveness probe endpoint.

        Returns:
            JSON status payload.
        """
        return {"status": "ok", "service": "rkgb"}

    return application


# Module-level app instance consumed by uvicorn and tests.
app: FastAPI = create_app()


def main() -> None:
    """Run the development server via the CLI entry point.

    Example::

        python -m app.main
        # or
        rkgb
    """
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # noqa: S104 — dev entrypoint only
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
