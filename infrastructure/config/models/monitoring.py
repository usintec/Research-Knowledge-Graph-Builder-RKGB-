"""Monitoring and observability configuration model."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PrometheusConfig(BaseModel):
    """Prometheus metrics exporter settings."""

    model_config = ConfigDict(frozen=True)

    enabled: bool = False
    metrics_path: str = "/metrics"
    port: int = Field(default=9090, ge=1, le=65535)


class OpenTelemetryConfig(BaseModel):
    """OpenTelemetry tracing and metrics settings."""

    model_config = ConfigDict(frozen=True)

    enabled: bool = False
    exporter_endpoint: str = "http://localhost:4317"
    service_name: str = "rkgb"
    service_version: str = "0.1.0"
    sample_rate: float = Field(default=1.0, ge=0.0, le=1.0)


class HealthCheckConfig(BaseModel):
    """Health check endpoint settings."""

    model_config = ConfigDict(frozen=True)

    enabled: bool = True
    path: str = "/health"
    include_details: bool = False  # Expose dependency health in response


class MonitoringConfig(BaseModel):
    """Unified monitoring and observability configuration."""

    model_config = ConfigDict(frozen=True)

    prometheus: PrometheusConfig = PrometheusConfig()
    otel: OpenTelemetryConfig = OpenTelemetryConfig()
    health: HealthCheckConfig = HealthCheckConfig()
    sentry_dsn: str = ""
