"""Application entry point.

This module bootstraps the RKGB platform.

Step A2 adds configuration system integration.  The ConfigManager is
bootstrapped during the FastAPI lifespan so all infrastructure components
receive their configuration via the DI container (Step A3).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from infrastructure.config.bootstrap import bootstrap_config
from infrastructure.config.manager import ConfigManager

# Module-level reference to the config manager — will be populated during lifespan.
_config_manager: ConfigManager | None = None


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


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """FastAPI lifespan — bootstraps and tears down application resources.

    Args:
        app: The FastAPI application instance.

    Yields:
        Control to the running application.
    """
    global _config_manager  # noqa: PLW0603

    # --- Startup ---
    _config_manager = bootstrap_config()
    root = _config_manager.root

    # Update the FastAPI app metadata from config (in case it differs from defaults)
    app.title = root.application.title
    app.version = root.application.version
    app.description = root.application.description

    yield

    # --- Shutdown ---
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
