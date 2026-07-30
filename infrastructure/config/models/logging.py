"""Logging configuration model."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LogFormat(StrEnum):
    """Supported log output formats."""

    CONSOLE = "console"
    JSON = "json"


class LogLevel(StrEnum):
    """Standard log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFileConfig(BaseModel):
    """File-based log sink settings."""

    model_config = ConfigDict(frozen=True)

    enabled: bool = False
    path: str = "logs/rkgb.log"
    max_bytes: int = Field(default=10 * 1024 * 1024, ge=1)  # 10 MB
    backup_count: int = Field(default=5, ge=0)

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Ensure the log file path is a valid non-empty string."""
        if not v.strip():
            raise ValueError("Log file path must not be empty.")
        return v


class LoggingConfig(BaseModel):
    """Complete logging configuration.

    Supports structlog with both human-readable console output for
    development and machine-parseable JSON for production log aggregation
    (e.g. Datadog, Loki, CloudWatch).  Future OpenTelemetry integration
    can be enabled via ``enable_otel``.
    """

    model_config = ConfigDict(frozen=True)

    level: LogLevel = LogLevel.INFO
    format: LogFormat = LogFormat.CONSOLE
    file: LogFileConfig = LogFileConfig()

    # Correlation / trace IDs injected into every log record
    include_correlation_id: bool = True
    include_pipeline_id: bool = True
    include_timestamp: bool = True
    include_caller: bool = False  # adds file:line info — useful in DEBUG mode

    # OpenTelemetry (future)
    enable_otel: bool = False
    otel_exporter_endpoint: str = ""

    # Suppress noisy third-party loggers in production
    suppress_third_party: bool = True

    @property
    def log_file_path(self) -> Path | None:
        """Return the resolved log file path, or ``None`` if file logging is off.

        Returns:
            ``Path`` instance or ``None``.
        """
        return Path(self.file.path) if self.file.enabled else None
