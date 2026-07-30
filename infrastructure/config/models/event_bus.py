"""Event bus configuration model."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class EventBusBackend(StrEnum):
    """Supported event bus backends."""

    IN_PROCESS = "in_process"  # Default: synchronous, in-memory
    KAFKA = "kafka"  # Future: distributed via Apache Kafka


class EventBusConfig(BaseModel):
    """Event bus configuration.

    The in-process backend dispatches events synchronously within the
    same process — suitable for development and single-instance deploys.
    The Kafka backend (future) supports distributed, durable event
    streaming across services.
    """

    model_config = ConfigDict(frozen=True)

    backend: EventBusBackend = EventBusBackend.IN_PROCESS
    max_queue_size: int = Field(default=10_000, ge=1)
    publish_timeout_seconds: float = Field(default=5.0, gt=0)
    enable_dead_letter_queue: bool = False
