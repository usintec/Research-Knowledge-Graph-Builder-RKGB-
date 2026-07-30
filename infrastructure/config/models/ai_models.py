"""AI model provider configuration models.

Provider-independent configuration for LLMs, embeddings, and other AI
services. Each provider has its own sub-config; the top-level
``AIModelsConfig`` selects which provider is active.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class AIProviderType(StrEnum):
    """Supported AI model providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    OLLAMA = "ollama"
    LOCAL_TRANSFORMERS = "local_transformers"
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    MOCK = "mock"  # For testing without real API calls


class OpenAIConfig(BaseModel):
    """OpenAI provider settings."""

    model_config = ConfigDict(frozen=True)

    api_key: str = ""
    model: str = "gpt-4o"
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1)
    timeout: float = Field(default=60.0, gt=0)
    max_retries: int = Field(default=3, ge=0)
    base_url: str = ""  # Override for compatible APIs (e.g. LiteLLM)


class AnthropicConfig(BaseModel):
    """Anthropic Claude provider settings."""

    model_config = ConfigDict(frozen=True)

    api_key: str = ""
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = Field(default=4096, ge=1)
    temperature: float = Field(default=0.0, ge=0.0, le=1.0)
    timeout: float = Field(default=60.0, gt=0)


class AzureOpenAIConfig(BaseModel):
    """Azure-hosted OpenAI settings."""

    model_config = ConfigDict(frozen=True)

    api_key: str = ""
    endpoint: str = ""
    deployment_name: str = ""
    api_version: str = "2024-02-01"


class OllamaConfig(BaseModel):
    """Ollama local model server settings."""

    model_config = ConfigDict(frozen=True)

    base_url: str = "http://localhost:11434"
    model: str = "llama3.2"
    timeout: float = Field(default=120.0, gt=0)


class LocalTransformersConfig(BaseModel):
    """HuggingFace Transformers local inference settings."""

    model_config = ConfigDict(frozen=True)

    model_name_or_path: str = ""
    device: str = "cpu"  # "cpu" | "cuda" | "mps"
    torch_dtype: str = "float32"


class AIModelsConfig(BaseModel):
    """Unified AI model configuration.

    Select the active provider via ``provider``; the corresponding
    sub-config will be used by the infrastructure adapters.
    """

    model_config = ConfigDict(frozen=True)

    provider: AIProviderType = AIProviderType.MOCK
    openai: OpenAIConfig = OpenAIConfig()
    anthropic: AnthropicConfig = AnthropicConfig()
    azure_openai: AzureOpenAIConfig = AzureOpenAIConfig()
    ollama: OllamaConfig = OllamaConfig()
    local_transformers: LocalTransformersConfig = LocalTransformersConfig()
