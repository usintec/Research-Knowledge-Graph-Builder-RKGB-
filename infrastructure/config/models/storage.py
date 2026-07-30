"""Storage configuration model."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StorageBackend(StrEnum):
    """Supported storage backends."""

    LOCAL = "local"
    S3 = "s3"
    GCS = "gcs"
    AZURE_BLOB = "azure_blob"
    MEMORY = "memory"  # In-memory; used in tests


class LocalStorageConfig(BaseModel):
    """Settings for the local filesystem backend."""

    model_config = ConfigDict(frozen=True)

    base_path: str = "./data/files"
    create_dirs: bool = True


class S3StorageConfig(BaseModel):
    """Settings for AWS S3-compatible storage."""

    model_config = ConfigDict(frozen=True)

    bucket_name: str = ""
    region: str = "us-east-1"
    endpoint_url: str = ""  # For S3-compatible stores (MinIO, etc.)
    access_key_id: str = ""
    secret_access_key: str = ""
    prefix: str = "rkgb/"


class StorageConfig(BaseModel):
    """Unified storage configuration.

    Selects a backend and carries the appropriate sub-configuration.
    Consumers should read ``backend`` first and then use the matching
    sub-config object.
    """

    model_config = ConfigDict(frozen=True)

    backend: StorageBackend = StorageBackend.LOCAL
    local: LocalStorageConfig = LocalStorageConfig()
    s3: S3StorageConfig = S3StorageConfig()
    max_file_size_mb: int = Field(default=100, ge=1)
    allowed_extensions: list[str] = Field(
        default_factory=lambda: [".pdf", ".txt", ".md", ".json"]
    )

    @field_validator("max_file_size_mb")
    @classmethod
    def validate_max_file_size(cls, v: int) -> int:
        """Guard against unreasonably large limits."""
        if v > 10_000:
            raise ValueError("max_file_size_mb must not exceed 10,000 MB (10 GB).")
        return v
