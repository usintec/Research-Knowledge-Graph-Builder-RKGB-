"""Neo4j database configuration model."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Neo4jAuthConfig(BaseModel):
    """Authentication credentials for Neo4j."""

    model_config = ConfigDict(frozen=True)

    username: str = "neo4j"
    password: str = ""


class Neo4jTLSConfig(BaseModel):
    """TLS settings for Neo4j connections."""

    model_config = ConfigDict(frozen=True)

    enabled: bool = False
    verify: bool = True
    cert_path: str = ""
    key_path: str = ""
    ca_path: str = ""


class Neo4jPoolConfig(BaseModel):
    """Connection pool settings."""

    model_config = ConfigDict(frozen=True)

    max_connection_lifetime: int = Field(default=3600, ge=0)
    max_connection_pool_size: int = Field(default=50, ge=1)
    connection_acquisition_timeout: float = Field(default=60.0, gt=0)
    liveness_check_timeout: float = Field(default=0.0, ge=0)


class Neo4jRetryConfig(BaseModel):
    """Retry policy for Neo4j operations."""

    model_config = ConfigDict(frozen=True)

    max_retries: int = Field(default=3, ge=0)
    retry_delay_seconds: float = Field(default=1.0, ge=0)
    backoff_multiplier: float = Field(default=2.0, ge=1.0)


class Neo4jConfig(BaseModel):
    """Complete Neo4j connection configuration.

    Supports both Bolt and HTTPS URIs, connection pooling, TLS, and retry.
    """

    model_config = ConfigDict(frozen=True)

    uri: str = "bolt://localhost:7687"
    database: str = "rkgb"
    auth: Neo4jAuthConfig = Neo4jAuthConfig()
    pool: Neo4jPoolConfig = Neo4jPoolConfig()
    retry: Neo4jRetryConfig = Neo4jRetryConfig()
    tls: Neo4jTLSConfig = Neo4jTLSConfig()
    query_timeout: float = Field(default=30.0, gt=0)
    fetch_size: int = Field(default=1000, ge=1)

    @field_validator("uri")
    @classmethod
    def validate_uri(cls, v: str) -> str:
        """Ensure the URI uses a supported Neo4j scheme."""
        supported = ("bolt://", "bolt+s://", "bolt+ssc://", "neo4j://", "neo4j+s://")
        if not any(v.startswith(s) for s in supported):
            raise ValueError(
                f"Neo4j URI must start with one of {supported}. Got: '{v}'"
            )
        return v
