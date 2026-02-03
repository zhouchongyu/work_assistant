"""
Application Configuration using pydantic-settings.

This module implements fail-fast configuration validation - the application
will fail to start if required configuration is missing or invalid.

Reference:
- assistant_py/config.py: Original configuration
- cool-admin-midway/src/config/config.default.ts: Node.js configuration
- Wiki: 系统架构/系统架构.md, 部署运维/基础设施配置/基础设施配置.md
"""

from functools import lru_cache
from typing import Any

from pydantic import Field, PostgresDsn, RedisDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """PostgreSQL database configuration."""

    model_config = SettingsConfigDict(env_prefix="PG")

    host: str = Field(..., alias="PGHOST", description="PostgreSQL host")
    port: int = Field(5432, alias="PGPORT", description="PostgreSQL port")
    user: str = Field(..., alias="PGUSER", description="PostgreSQL user")
    password: str = Field(..., alias="PGPASSWORD", description="PostgreSQL password")
    database: str = Field(..., alias="PGDATABASE", description="PostgreSQL database name")

    @property
    def async_url(self) -> str:
        """Generate async PostgreSQL connection URL."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    @property
    def sync_url(self) -> str:
        """Generate sync PostgreSQL connection URL."""
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class RedisSettings(BaseSettings):
    """Redis configuration."""

    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str = Field(..., description="Redis host")
    port: int = Field(6379, description="Redis port")
    db: int = Field(0, description="Redis database number")
    password: str | None = Field(None, alias="REDIS_KEY", description="Redis password")

    @property
    def url(self) -> str:
        """Generate Redis connection URL."""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class RabbitMQSettings(BaseSettings):
    """RabbitMQ configuration."""

    model_config = SettingsConfigDict(env_prefix="RABBIT_")

    broker_url: str = Field(..., description="RabbitMQ broker URL")
    heartbeat: int = Field(600, description="RabbitMQ heartbeat interval")
    max_consumers: int = Field(1, description="Maximum concurrent consumers per queue")

    @property
    def full_url(self) -> str:
        """Generate full broker URL with heartbeat."""
        separator = "&" if "?" in self.broker_url else "?"
        return f"{self.broker_url}{separator}heartbeat={self.heartbeat}"


class MQTTSettings(BaseSettings):
    """MQTT broker configuration."""

    model_config = SettingsConfigDict(env_prefix="MQTT_")

    broker_host: str = Field("localhost", description="MQTT broker host")
    broker_port: int = Field(1883, description="MQTT broker port")
    username: str | None = Field(None, description="MQTT username")
    password: str | None = Field(None, description="MQTT password")
    client_id_prefix: str = Field("work-assistant-v2", description="MQTT client ID prefix")
    keepalive: int = Field(60, description="MQTT keepalive interval")
    protocol_version: int = Field(5, description="MQTT protocol version")


class AzureSettings(BaseSettings):
    """Azure service configuration."""

    model_config = SettingsConfigDict(env_prefix="AZURE_")

    # Azure AD / Graph API (for SharePoint operations)
    tenant_id: str | None = Field(None, description="Azure tenant ID")
    client_id: str | None = Field(None, description="Azure client ID")
    client_secret: str | None = Field(None, description="Azure client secret")
    drive_id: str | None = Field(None, description="SharePoint drive ID")
    supply_path: str | None = Field(None, description="Supply folder path in SharePoint")

    # Azure Blob Storage
    storage_connection_string: str | None = Field(None, description="Azure Storage connection string")
    storage_container_resume: str | None = Field(
        None,
        alias="AZURE_STORAGE_CONTAINER_NAME_RESUME",
        description="Resume container name"
    )

    # Azure Email
    send_email: str | None = Field(None, description="Sender email address")
    email_tenant_id: str | None = Field(None, description="Email tenant ID")
    email_client_id: str | None = Field(None, description="Email client ID")
    email_client_secret: str | None = Field(None, description="Email client secret")

    # MSAL (for delegated Graph API - Teams, Email via user context)
    msal_tenant_id: str | None = Field(None, alias="MSAL_AUTHORITY_ID", description="MSAL tenant/authority ID")
    msal_client_id: str | None = Field(None, alias="MSAL_CLIENT_ID", description="MSAL client ID")
    msal_client_secret: str | None = Field(None, alias="MSAL_BACKEND_CLIENT_SECRET", description="MSAL client secret")


class AISettings(BaseSettings):
    """AI and LLM service configuration."""

    model_config = SettingsConfigDict(env_prefix="")

    openai_url: str | None = Field(None, alias="OPENAI_URL", description="OpenAI API URL")
    third_party_analyze_url: str | None = Field(None, alias="THIRD_PARTY_ANALYZE_URL", description="Third-party analysis service URL")
    callback_base_url: str | None = Field(None, alias="CALLBACK_BASE_URL", description="Callback base URL for async operations")

    # Dify configuration
    dify_api_base_url: str | None = Field(None, alias="DIFY_API_BASE_URL", description="Dify API base URL")
    dify_api_key: str | None = Field(None, alias="DIFY_API_KEY", description="Dify API key")


class JWTSettings(BaseSettings):
    """JWT authentication configuration."""

    model_config = SettingsConfigDict(env_prefix="JWT_")

    secret_key: str = Field(..., description="JWT secret key for signing tokens")
    algorithm: str = Field("HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(30, description="Access token expiration in minutes")
    refresh_token_expire_days: int = Field(7, description="Refresh token expiration in days")


class AppSettings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application
    app_name: str = Field("Work Assistant V2", description="Application name")
    app_version: str = Field("2.0.0", description="Application version")
    debug: bool = Field(False, description="Debug mode")
    environment: str = Field("development", description="Environment (development/staging/production)")

    # Server
    host: str = Field("0.0.0.0", description="Server host")
    port: int = Field(8000, description="Server port")

    # API
    api_v1_prefix: str = Field("/api/v1", description="API v1 prefix")

    # CORS
    cors_origins: list[str] = Field(["*"], description="Allowed CORS origins")

    # Kong (API Gateway)
    kong_name: str | None = Field(None, alias="KONG_NAME", description="Kong service name")
    kong_auth: str | None = Field(None, alias="KONG_AUTH", description="Kong auth header")

    # File paths
    local_path: str = Field("", alias="LOCAL_PATH", description="Local file path")
    local_flag: int = Field(0, alias="LOCAL_FLAG", description="Local flag")

    # Supply base URL
    supply_base_url: str | None = Field(None, alias="SUPPLY_BASE_URL", description="Supply base URL")

    # Office viewer
    office_viewer_url: str = Field(
        "https://view.officeapps.live.com/op/view.aspx?src=",
        description="Office viewer URL prefix"
    )

    # Nested settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    rabbitmq: RabbitMQSettings = Field(default_factory=RabbitMQSettings)
    mqtt: MQTTSettings = Field(default_factory=MQTTSettings)
    azure: AzureSettings = Field(default_factory=AzureSettings)
    ai: AISettings = Field(default_factory=AISettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)

    @model_validator(mode="after")
    def validate_critical_settings(self) -> "AppSettings":
        """
        Fail-fast validation for critical configuration.

        This validator ensures the application fails to start if critical
        configuration is missing, rather than failing at runtime.
        """
        errors: list[str] = []

        # Database is always required
        if not self.database.host:
            errors.append("PGHOST is required")
        if not self.database.user:
            errors.append("PGUSER is required")
        if not self.database.password:
            errors.append("PGPASSWORD is required")
        if not self.database.database:
            errors.append("PGDATABASE is required")

        # Redis is always required
        if not self.redis.host:
            errors.append("REDIS_HOST is required")

        # RabbitMQ is required for async operations
        if not self.rabbitmq.broker_url:
            errors.append("RABBIT_BROKER_URL is required")

        # JWT secret is required for authentication
        if not self.jwt.secret_key:
            errors.append("JWT_SECRET_KEY is required")

        # In production, additional validation
        if self.environment == "production":
            if self.debug:
                errors.append("DEBUG must be False in production")
            if "*" in self.cors_origins:
                errors.append("CORS_ORIGINS cannot be '*' in production")

        if errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

        return self


@lru_cache
def get_settings() -> AppSettings:
    """
    Get cached application settings.

    Uses lru_cache to ensure settings are only loaded once.
    The application will fail to start if required configuration is missing.
    """
    return AppSettings()


# Export settings instance for convenience
settings = get_settings()
