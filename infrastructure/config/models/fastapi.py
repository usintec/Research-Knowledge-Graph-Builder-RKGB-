"""FastAPI framework configuration model."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class FastAPIDocsConfig(BaseModel):
    """OpenAPI documentation settings."""

    model_config = ConfigDict(frozen=True)

    enabled: bool = True
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"


class FastAPIMiddlewareConfig(BaseModel):
    """Middleware configuration."""

    model_config = ConfigDict(frozen=True)

    enable_gzip: bool = True
    gzip_minimum_size: int = Field(default=1000, ge=0)
    enable_trusted_host: bool = False
    enable_request_id: bool = True
    enable_process_time_header: bool = True


class FastAPIConfig(BaseModel):
    """FastAPI application framework configuration.

    Separated from ApplicationConfig so that framework-level concerns
    (docs, middleware, timeouts) can evolve independently of domain
    application settings.
    """

    model_config = ConfigDict(frozen=True)

    docs: FastAPIDocsConfig = FastAPIDocsConfig()
    middleware: FastAPIMiddlewareConfig = FastAPIMiddlewareConfig()
    request_timeout_seconds: float = Field(default=30.0, gt=0)
    max_request_size_mb: int = Field(default=50, ge=1)
    root_path: str = ""  # Set when behind a reverse proxy with a path prefix
    api_prefix: str = "/api/v1"
