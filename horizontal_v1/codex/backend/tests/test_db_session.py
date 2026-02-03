from backend.app.core.settings import Settings


def test_create_async_engine_uses_database_url():
    from backend.app.db.session import create_async_engine_from_settings

    settings = Settings(
        database_url="postgresql+asyncpg://user:pass@localhost:5432/work_assistant_v3",
        redis_url="redis://localhost:6379/0",
    )

    engine = create_async_engine_from_settings(settings)
    assert engine.url.render_as_string(hide_password=False) == settings.database_url

