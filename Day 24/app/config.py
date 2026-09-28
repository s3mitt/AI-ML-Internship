"""Application Configuration using Pydantic Settings.

Manages environment variable validation, type casting, secrets handling,
and environment-specific overrides following 12-factor application standards.
"""

from functools import lru_cache
from typing import List
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application Settings with strict validation and safe secrets masking."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Core Application Configuration
    APP_NAME: str = Field(default="Linkific Production Service", description="Application service name")
    APP_ENV: str = Field(default="development", description="Deployment environment")
    APP_DEBUG: bool = Field(default=False, description="Debug mode flag")
    APP_VERSION: str = Field(default="1.0.0", description="Semantic service version")

    # Networking Configuration
    HOST: str = Field(default="0.0.0.0", description="Network interface binding")
    PORT: int = Field(default=8000, ge=1, le=65535, description="Port number")

    # Observability & Logging
    LOG_LEVEL: str = Field(default="INFO", description="Minimum log level threshold")
    LOG_FORMAT: str = Field(default="json", description="Log format: json or text")

    # Security Configuration
    API_SECRET_KEY: SecretStr = Field(
        default=SecretStr("default-insecure-dev-secret-change-in-prod"),
        description="Application secret key masked in string representations",
    )
    ALLOWED_ORIGINS: str = Field(default="*", description="Comma-separated CORS origins")

    # Metrics & Monitoring Configuration
    METRICS_ENABLED: bool = Field(default=True, description="Enable Prometheus metrics endpoint")
    ENABLE_SYSTEM_TELEMETRY: bool = Field(default=True, description="Enable system-level telemetry tracking")
    RATE_LIMIT_PER_MINUTE: int = Field(default=120, ge=1, description="Rate limit per client window")

    @field_validator("APP_ENV")
    @classmethod
    def validate_app_env(cls, value: str) -> str:
        """Ensure deployment environment is one of the allowed stages."""
        allowed = {"development", "staging", "production", "testing"}
        v_lower = value.lower()
        if v_lower not in allowed:
            raise ValueError(f"Invalid APP_ENV '{value}'. Allowed: {', '.join(allowed)}")
        return v_lower

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        """Ensure log level conforms to standard logging severity levels."""
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = value.upper()
        if v_upper not in allowed:
            raise ValueError(f"Invalid LOG_LEVEL '{value}'. Allowed: {', '.join(allowed)}")
        return v_upper

    @field_validator("LOG_FORMAT")
    @classmethod
    def validate_log_format(cls, value: str) -> str:
        """Ensure log format is either structured json or human-readable text."""
        allowed = {"json", "text"}
        v_lower = value.lower()
        if v_lower not in allowed:
            raise ValueError(f"Invalid LOG_FORMAT '{value}'. Allowed: {', '.join(allowed)}")
        return v_lower

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated allowed origins into a list."""
        if not self.ALLOWED_ORIGINS or self.ALLOWED_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        """Check if current environment is set to production."""
        return self.APP_ENV == "production"


@lru_cache()
def get_settings() -> Settings:
    """Retrieve cached application settings instance."""
    return Settings()
