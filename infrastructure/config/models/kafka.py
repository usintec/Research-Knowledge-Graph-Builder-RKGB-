"""Kafka configuration model (future integration)."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class KafkaSecurityProtocol(StrEnum):
    """Kafka security protocols."""

    PLAINTEXT = "PLAINTEXT"
    SSL = "SSL"
    SASL_PLAINTEXT = "SASL_PLAINTEXT"
    SASL_SSL = "SASL_SSL"


class KafkaProducerConfig(BaseModel):
    """Kafka producer settings."""

    model_config = ConfigDict(frozen=True)

    acks: str = "all"
    retries: int = Field(default=3, ge=0)
    batch_size: int = Field(default=16384, ge=0)
    linger_ms: int = Field(default=0, ge=0)
    compression_type: str = "gzip"
    max_in_flight_requests_per_connection: int = Field(default=5, ge=1)


class KafkaConsumerConfig(BaseModel):
    """Kafka consumer settings."""

    model_config = ConfigDict(frozen=True)

    group_id: str = "rkgb-consumers"
    auto_offset_reset: str = "earliest"
    enable_auto_commit: bool = False
    max_poll_records: int = Field(default=500, ge=1)
    session_timeout_ms: int = Field(default=30000, ge=1)


class KafkaConfig(BaseModel):
    """Apache Kafka configuration.

    Only required when ``EventBusConfig.backend`` is set to ``kafka``.
    """

    model_config = ConfigDict(frozen=True)

    bootstrap_servers: list[str] = Field(default_factory=lambda: ["localhost:9092"])
    topic_prefix: str = "rkgb."
    security_protocol: KafkaSecurityProtocol = KafkaSecurityProtocol.PLAINTEXT
    producer: KafkaProducerConfig = KafkaProducerConfig()
    consumer: KafkaConsumerConfig = KafkaConsumerConfig()
    request_timeout_ms: int = Field(default=30000, ge=1)
    ssl_cafile: str = ""
    ssl_certfile: str = ""
    ssl_keyfile: str = ""
