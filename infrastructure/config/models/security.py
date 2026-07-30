"""Security configuration model."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AuthScheme(StrEnum):
    """Supported authentication schemes."""

    NONE = "none"
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"


class JWTConfig(BaseModel):
    """JSON Web Token settings."""

    model_config = ConfigDict(frozen=True)

    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, ge=1)
    refresh_token_expire_days: int = Field(default=7, ge=1)
    issuer: str = "rkgb"


class APIKeyConfig(BaseModel):
    """API key authentication settings."""

    model_config = ConfigDict(frozen=True)

    header_name: str = "X-API-Key"
    query_param_name: str = "api_key"


class SecurityConfig(BaseModel):
    """Security and authentication configuration."""

    model_config = ConfigDict(frozen=True)

    scheme: AuthScheme = AuthScheme.NONE
    jwt: JWTConfig = JWTConfig()
    api_key: APIKeyConfig = APIKeyConfig()

    # HTTPS / TLS
    https_only: bool = False
    hsts_max_age: int = Field(default=31536000, ge=0)  # 1 year

    # Rate limiting
    rate_limit_enabled: bool = False
    rate_limit_requests_per_minute: int = Field(default=60, ge=1)

    # CORS
    cors_enabled: bool = True
    cors_allow_credentials: bool = False

    @field_validator("scheme", mode="before")
    @classmethod
    def normalise_scheme(cls, v: object) -> object:
        """Accept lowercase scheme strings."""
        if isinstance(v, str):
            return v.lower()
        return v
