from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="WA_", extra="ignore")

    database_url: str = Field(min_length=1)
    redis_url: str = Field(min_length=1)
    jwt_secret: str = Field(min_length=1)

    # SharePoint / Graph (client-credentials / daemon mode for v1)
    graph_tenant_id: str = Field(min_length=1)
    graph_client_id: str = Field(min_length=1)
    graph_client_secret: str = Field(min_length=1)
    graph_drive_id: str = Field(min_length=1)
    graph_supply_path: str = Field(min_length=1)

    # Third-party analyze (request-callback model)
    third_party_analyze_url: str = Field(min_length=1)
    callback_base_url: str = Field(min_length=1)
    third_party_callback_token: str | None = None
    third_party_timeout_seconds: float = 30.0

    # Dify (chat mode only)
    dify_api_base_url: str = Field(min_length=1)
    dify_api_key: str = Field(min_length=1)
    dify_app_mode: Literal["chat"] = "chat"
    dify_timeout_ms: int = 60_000

    access_token_expire_seconds: int = 2 * 3600
    refresh_token_expire_seconds: int = 24 * 3600 * 15

    db_schema: str = "wa_v3"
    environment: str = "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
