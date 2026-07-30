"""Vector database configuration model.

Only the configuration framework is required at this stage.
No implementations are provided here.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class VectorStoreBackend(StrEnum):
    """Supported vector database backends."""

    FAISS = "faiss"
    QDRANT = "qdrant"
    MILVUS = "milvus"
    WEAVIATE = "weaviate"
    CHROMA = "chroma"
    PINECONE = "pinecone"
    MEMORY = "memory"  # In-process; for testing


class QdrantConfig(BaseModel):
    """Qdrant vector database settings."""

    model_config = ConfigDict(frozen=True)

    url: str = "http://localhost:6333"
    api_key: str = ""
    collection_name: str = "rkgb_documents"
    timeout: float = Field(default=30.0, gt=0)


class ChromaConfig(BaseModel):
    """Chroma vector database settings."""

    model_config = ConfigDict(frozen=True)

    host: str = "localhost"
    port: int = Field(default=8000, ge=1, le=65535)
    collection_name: str = "rkgb_documents"
    persist_directory: str = "./data/chroma"


class PineconeConfig(BaseModel):
    """Pinecone vector database settings."""

    model_config = ConfigDict(frozen=True)

    api_key: str = ""
    environment: str = ""
    index_name: str = "rkgb"
    namespace: str = ""


class VectorStoreConfig(BaseModel):
    """Unified vector database configuration.

    The ``backend`` field selects which vector store is active.
    Only the corresponding sub-config needs to be populated.
    """

    model_config = ConfigDict(frozen=True)

    backend: VectorStoreBackend = VectorStoreBackend.MEMORY
    qdrant: QdrantConfig = QdrantConfig()
    chroma: ChromaConfig = ChromaConfig()
    pinecone: PineconeConfig = PineconeConfig()
    faiss_index_path: str = "./data/faiss"
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    top_k: int = Field(default=10, ge=1)
