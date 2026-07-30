"""Embedding model configuration."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class EmbeddingProviderType(StrEnum):
    """Supported embedding providers."""

    OPENAI = "openai"
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    AZURE_OPENAI = "azure_openai"
    OLLAMA = "ollama"
    MOCK = "mock"


class EmbeddingsConfig(BaseModel):
    """Embedding generation configuration.

    Embeddings are used for semantic similarity, vector store indexing,
    and GraphRAG retrieval augmentation.
    """

    model_config = ConfigDict(frozen=True)

    provider: EmbeddingProviderType = EmbeddingProviderType.MOCK
    model: str = "text-embedding-3-small"
    dimension: int = Field(default=1536, ge=1)
    batch_size: int = Field(default=100, ge=1)
    normalize: bool = True
    cache_embeddings: bool = True
