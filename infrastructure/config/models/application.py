"""Application-level configuration model."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from infrastructure.config.environment import Environment


class ApplicationConfig(BaseModel):
    """Top-level application configuration.

    Design note: Pydantic BaseModel with ``frozen=True`` is chosen over a
    plain dataclass because it provides runtime validation, IDE-friendly
    field introspection, and JSON-schema generation for free.  Immutability
    (``frozen=True``) is enforced so consumers cannot accidentally mutate
    shared configuration state.
    """

    model_config = ConfigDict(frozen=True)

    env: Environment = Environment.DEVELOPMENT
    debug: bool = False
    host: str = "0.0.0.0"  # noqa: S104
    port: int = Field(default=8000, ge=1, le=65535)
    workers: int = Field(default=1, ge=1)
    reload: bool = False
    title: str = "Research Knowledge Graph Builder"
    version: str = "0.1.0"
    description: str = (
        "Enterprise AI platform for scientific knowledge extraction "
        "and GraphRAG-powered research intelligence."
    )
    allowed_hosts: list[str] = Field(default_factory=lambda: ["*"])
    cors_origins: list[str] = Field(default_factory=list)

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Reject privileged ports unless running as root."""
        if v < 1024:
            import os

            if os.getuid() != 0:  # type: ignore[attr-defined]
                raise ValueError(
                    f"Port {v} is privileged (< 1024). "
                    "Use a port ≥ 1024 or run as root."
                )
        return v
