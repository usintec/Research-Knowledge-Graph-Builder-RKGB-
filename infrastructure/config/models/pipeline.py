"""Pipeline and processing engine configuration models."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ExecutionStrategy(StrEnum):
    """Pipeline stage execution strategies."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


class PipelineRetryConfig(BaseModel):
    """Per-pipeline retry settings."""

    model_config = ConfigDict(frozen=True)

    max_retries: int = Field(default=3, ge=0)
    retry_delay_seconds: float = Field(default=1.0, ge=0)
    backoff_multiplier: float = Field(default=2.0, ge=1.0)


class PipelineConfig(BaseModel):
    """Configuration for a single pipeline.

    Each of the twelve domain pipelines can carry its own independent
    configuration.  These values are not hardcoded — they are loaded
    from YAML and injectable via the DI container.
    """

    model_config = ConfigDict(frozen=True)

    enabled: bool = True
    execution_strategy: ExecutionStrategy = ExecutionStrategy.SEQUENTIAL
    timeout_seconds: float = Field(default=300.0, gt=0)
    max_concurrent_runs: int = Field(default=1, ge=1)
    checkpoint_interval: int = Field(default=0, ge=0)  # 0 = disabled
    enable_metrics: bool = True
    retry: PipelineRetryConfig = PipelineRetryConfig()


class ProcessingEngineConfig(BaseModel):
    """Global processing engine configuration.

    Controls the pipeline runtime that orchestrates all twelve domain
    pipelines.  Individual pipelines can override these defaults via
    their own ``PipelineConfig``.
    """

    model_config = ConfigDict(frozen=True)

    max_parallel_pipelines: int = Field(default=4, ge=1)
    worker_pool_size: int = Field(default=4, ge=1)
    default_timeout_seconds: float = Field(default=300.0, gt=0)
    enable_plugin_loader: bool = False
    plugin_scan_paths: list[str] = Field(default_factory=list)

    # Per-pipeline overrides — keyed by pipeline name
    pipelines: dict[str, PipelineConfig] = Field(default_factory=dict)
