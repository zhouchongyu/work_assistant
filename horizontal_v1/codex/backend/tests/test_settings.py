import pytest
from pydantic import ValidationError


def test_settings_fail_fast_when_required_env_missing(monkeypatch):
    monkeypatch.delenv("WA_DATABASE_URL", raising=False)
    monkeypatch.delenv("WA_REDIS_URL", raising=False)
    monkeypatch.delenv("WA_JWT_SECRET", raising=False)

    from backend.app.core.settings import Settings

    with pytest.raises(ValidationError):
        Settings()


def test_settings_fail_fast_when_graph_env_missing(monkeypatch):
    monkeypatch.setenv("WA_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("WA_REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("WA_JWT_SECRET", "test-secret")
    monkeypatch.setenv("WA_THIRD_PARTY_ANALYZE_URL", "http://third-party.example")
    monkeypatch.setenv("WA_CALLBACK_BASE_URL", "http://backend.example/api/v1/resume/analyze/callback")
    monkeypatch.setenv("WA_DIFY_API_BASE_URL", "http://dify.example/v1")
    monkeypatch.setenv("WA_DIFY_API_KEY", "test-key")

    monkeypatch.delenv("WA_GRAPH_TENANT_ID", raising=False)
    monkeypatch.delenv("WA_GRAPH_CLIENT_ID", raising=False)
    monkeypatch.delenv("WA_GRAPH_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("WA_GRAPH_DRIVE_ID", raising=False)
    monkeypatch.delenv("WA_GRAPH_SUPPLY_PATH", raising=False)

    from backend.app.core.settings import Settings

    with pytest.raises(ValidationError):
        Settings()


def test_settings_fail_fast_when_third_party_env_missing(monkeypatch):
    monkeypatch.setenv("WA_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("WA_REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("WA_JWT_SECRET", "test-secret")
    monkeypatch.setenv("WA_DIFY_API_BASE_URL", "http://dify.example/v1")
    monkeypatch.setenv("WA_DIFY_API_KEY", "test-key")
    monkeypatch.setenv("WA_GRAPH_TENANT_ID", "tenant")
    monkeypatch.setenv("WA_GRAPH_CLIENT_ID", "client")
    monkeypatch.setenv("WA_GRAPH_CLIENT_SECRET", "secret")
    monkeypatch.setenv("WA_GRAPH_DRIVE_ID", "drive")
    monkeypatch.setenv("WA_GRAPH_SUPPLY_PATH", "/supply")

    monkeypatch.delenv("WA_THIRD_PARTY_ANALYZE_URL", raising=False)
    monkeypatch.delenv("WA_CALLBACK_BASE_URL", raising=False)

    from backend.app.core.settings import Settings

    with pytest.raises(ValidationError):
        Settings()


def test_settings_fail_fast_when_dify_env_missing(monkeypatch):
    monkeypatch.setenv("WA_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("WA_REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("WA_JWT_SECRET", "test-secret")
    monkeypatch.setenv("WA_THIRD_PARTY_ANALYZE_URL", "http://third-party.example")
    monkeypatch.setenv("WA_CALLBACK_BASE_URL", "http://backend.example/api/v1/resume/analyze/callback")
    monkeypatch.setenv("WA_GRAPH_TENANT_ID", "tenant")
    monkeypatch.setenv("WA_GRAPH_CLIENT_ID", "client")
    monkeypatch.setenv("WA_GRAPH_CLIENT_SECRET", "secret")
    monkeypatch.setenv("WA_GRAPH_DRIVE_ID", "drive")
    monkeypatch.setenv("WA_GRAPH_SUPPLY_PATH", "/supply")

    monkeypatch.delenv("WA_DIFY_API_BASE_URL", raising=False)
    monkeypatch.delenv("WA_DIFY_API_KEY", raising=False)

    from backend.app.core.settings import Settings

    with pytest.raises(ValidationError):
        Settings()


def test_create_app_fail_fast_when_required_env_missing(monkeypatch):
    monkeypatch.delenv("WA_DATABASE_URL", raising=False)
    monkeypatch.delenv("WA_REDIS_URL", raising=False)
    monkeypatch.delenv("WA_JWT_SECRET", raising=False)

    from backend.app.core.settings import get_settings
    get_settings.cache_clear()

    from backend.app.main import create_app

    with pytest.raises(ValidationError):
        create_app()
