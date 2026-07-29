"""Application entry point.

This module bootstraps the RKGB platform.

In Step A1 this is a minimal placeholder that confirms the package
structure is importable and the server can be started. Full bootstrap
logic (DI container, lifespan hooks, router registration) will be
implemented in subsequent steps.
"""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI


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
