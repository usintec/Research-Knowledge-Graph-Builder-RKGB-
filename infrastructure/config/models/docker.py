"""Docker / containerisation configuration model."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class DockerConfig(BaseModel):
    """Docker deployment configuration.

    Carries values relevant when the application is running inside
    a container — e.g. for health-check scripts or service discovery.
    """

    model_config = ConfigDict(frozen=True)

    container_name: str = "rkgb-app"
    network_name: str = "rkgb-net"
    neo4j_service_name: str = "neo4j"
    redis_service_name: str = "redis"
    internal_port: int = 8000
