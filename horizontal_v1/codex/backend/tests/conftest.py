from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest
import uuid

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


os.environ.setdefault(
    "WA_DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/work_assistant_v3"
)
os.environ.setdefault("WA_REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("WA_JWT_SECRET", "dev-secret")
os.environ.setdefault("WA_GRAPH_TENANT_ID", "test-tenant")
os.environ.setdefault("WA_GRAPH_CLIENT_ID", "test-client-id")
os.environ.setdefault("WA_GRAPH_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault("WA_GRAPH_DRIVE_ID", "test-drive-id")
os.environ.setdefault("WA_GRAPH_SUPPLY_PATH", "/supply")
os.environ.setdefault("WA_THIRD_PARTY_ANALYZE_URL", "http://third-party.example")
os.environ.setdefault("WA_CALLBACK_BASE_URL", "http://backend.example/api/v1/resume/analyze/callback")
os.environ.setdefault("WA_DIFY_API_BASE_URL", "http://dify.example/v1")
os.environ.setdefault("WA_DIFY_API_KEY", "test-dify-key")


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def app(monkeypatch):
    # Use SQLite for tests (no external services).
    monkeypatch.setenv("WA_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("WA_REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("WA_JWT_SECRET", "test-secret")
    monkeypatch.setenv("WA_GRAPH_TENANT_ID", "test-tenant")
    monkeypatch.setenv("WA_GRAPH_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("WA_GRAPH_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setenv("WA_GRAPH_DRIVE_ID", "test-drive-id")
    monkeypatch.setenv("WA_GRAPH_SUPPLY_PATH", "/supply")
    monkeypatch.setenv("WA_THIRD_PARTY_ANALYZE_URL", "http://third-party.example")
    monkeypatch.setenv("WA_CALLBACK_BASE_URL", "http://backend.example/api/v1/resume/analyze/callback")
    monkeypatch.setenv("WA_DIFY_API_BASE_URL", "http://dify.example/v1")
    monkeypatch.setenv("WA_DIFY_API_KEY", "test-dify-key")
    tmp_dir = tempfile.TemporaryDirectory()
    monkeypatch.setenv("WA_FILE_STORAGE_DIR", tmp_dir.name)

    from backend.app.core.settings import get_settings
    from backend.app.db.session import get_async_engine
    from backend.app.integrations.redis_client import get_redis
    from backend.app.integrations.sharepoint_graph.client import GraphDriveItem, get_graph_client
    from backend.app.integrations.third_party_analyze.client import get_third_party_analyze_client
    from backend.app.integrations.dify.client import get_dify_client

    get_settings.cache_clear()
    get_async_engine.cache_clear()
    get_redis.cache_clear()

    from backend.app.main import create_app
    from backend.app.db.base import Base
    from backend.app.db.session import get_async_sessionmaker

    # Import models to register metadata before create_all()
    import backend.app.models  # noqa: F401

    # Build app
    fastapi_app = create_app()

    # Create schema
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed: admin role + user + user_role
    from backend.app.models.sys_role import SysRole
    from backend.app.models.sys_user import SysUser
    from backend.app.models.sys_user_role import SysUserRole
    from backend.app.services.auth_service import hash_password

    async_session = get_async_sessionmaker()
    async with async_session() as session:
        admin_role = SysRole(name="admin", label="admin")
        session.add(admin_role)
        await session.flush()

        admin_user = SysUser(
            username="admin",
            password_hash=hash_password("admin123"),
            status=1,
            password_version=1,
            name="Admin",
        )
        session.add(admin_user)
        await session.flush()

        session.add(SysUserRole(user_id=admin_user.id, role_id=admin_role.id))
        await session.commit()

    # Override redis dependency with fakeredis
    import fakeredis.aioredis

    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)

    async def _override_get_redis():
        return fake_redis

    fastapi_app.dependency_overrides[get_redis] = _override_get_redis
    fastapi_app.state._test_redis = fake_redis

    # Override Graph client to avoid real network calls.
    class _FakeGraphClient:
        def __init__(self):
            self._folders: dict[str, str] = {}
            self._files: dict[str, tuple[bytes, str | None, str]] = {}

        async def create_folder(self, folder_name: str) -> dict:
            folder_id = self._folders.get(folder_name) or f"folder-{uuid.uuid4().hex}"
            self._folders[folder_name] = folder_id
            return {"id": folder_id, "url": f"https://sharepoint.test/{folder_id}"}

        async def ensure_child_folder(self, parent_id: str, folder_name: str) -> dict:
            folder_id = f"{parent_id}/{folder_name}"
            self._folders[f"{parent_id}:{folder_name}"] = folder_id
            return {"id": folder_id, "webUrl": f"https://sharepoint.test/{folder_id}"}

        async def upload_file(self, folder_id: str, file_name: str, file_content: bytes, content_type: str | None) -> dict:
            file_id = f"file-{uuid.uuid4().hex}"
            self._files[file_id] = (file_content, content_type, file_name)
            return {"id": file_id, "name": file_name, "webUrl": f"https://sharepoint.test/{folder_id}/{file_name}"}

        async def update_file(self, file_id: str, file_content: bytes, content_type: str | None) -> dict:
            _, _, old_name = self._files.get(file_id) or (b"", None, "file")
            self._files[file_id] = (file_content, content_type, old_name)
            return {"id": file_id, "name": old_name, "webUrl": f"https://sharepoint.test/file/{file_id}"}

        async def create_link(self, item_id: str) -> str:
            return f"https://sharepoint.test/share/{item_id}"

        async def change_folder_name(self, folder_id: str, new_name: str) -> str:
            _ = new_name
            return f"https://sharepoint.test/{folder_id}"

        async def move_file(self, file_id: str, new_folder_id: str) -> None:
            _ = file_id, new_folder_id

        async def change_file_name(self, file_id: str, new_name: str) -> str:
            content, content_type, _old = self._files.get(file_id) or (b"", None, "file")
            self._files[file_id] = (content, content_type, new_name)
            return f"https://sharepoint.test/file/{file_id}"

        async def delete_file(self, file_id: str) -> None:
            self._files.pop(file_id, None)

        async def get_drive_item(self, file_id: str) -> GraphDriveItem:
            content, content_type, name = self._files.get(file_id) or (b"", None, "")
            _ = content
            return GraphDriveItem(id=file_id, name=name, web_url=f"https://sharepoint.test/file/{file_id}", content_type=content_type)

        async def stream_file_content(self, file_id: str):
            content, _, _ = self._files.get(file_id) or (b"", None, "")

            async def _iter():
                yield content

            return _iter()

    fake_graph = _FakeGraphClient()

    def _override_get_graph_client():
        return fake_graph

    fastapi_app.dependency_overrides[get_graph_client] = _override_get_graph_client
    fastapi_app.state._test_graph = fake_graph

    class _FakeThirdPartyAnalyzeClient:
        def __init__(self):
            self.calls: dict[str, list[dict]] = {
                "analyze_resume": [],
                "analyze_resume_proposal": [],
                "analyze_demand_txt": [],
                "analyze_match": [],
                "analyze_similar": [],
                "hard_condition": [],
            }

        async def analyze_resume(self, **kwargs):
            self.calls["analyze_resume"].append(kwargs)
            return "req-resume"

        async def analyze_resume_proposal(self, **kwargs):
            self.calls["analyze_resume_proposal"].append(kwargs)
            return "req-proposal"

        async def analyze_demand_txt(self, **kwargs):
            self.calls["analyze_demand_txt"].append(kwargs)
            return "req-demand"

        async def analyze_match(self, **kwargs):
            self.calls["analyze_match"].append(kwargs)
            return "req-match"

        async def analyze_similar(self, **kwargs):
            self.calls["analyze_similar"].append(kwargs)
            return {"result": {"score": 0}}

        async def hard_condition(self, **kwargs):
            self.calls["hard_condition"].append(kwargs)
            return {"msg": []}

    fake_third_party = _FakeThirdPartyAnalyzeClient()

    def _override_get_third_party_analyze_client():
        return fake_third_party

    fastapi_app.dependency_overrides[get_third_party_analyze_client] = _override_get_third_party_analyze_client
    fastapi_app.state._test_third_party = fake_third_party

    class _FakeDifyClient:
        async def chat_blocking(self, **kwargs):
            _ = kwargs
            from backend.app.integrations.dify.client import DifyChatResult

            return DifyChatResult(answer="hi-blocking", conversation_id="c-test", message_id="m-test", raw={})

        async def chat_streaming(self, **kwargs):
            _ = kwargs

            async def _iter():
                yield b"chunk-1"
                yield b"chunk-2"

            return _iter()

        async def list_conversations(self, **kwargs):
            _ = kwargs
            return {"data": [{"id": "c-test", "title": "Conversation", "created_at": 1}]}

        async def list_messages(self, **kwargs):
            _ = kwargs
            return {"data": [{"id": "m-test", "query": "hi", "answer": "hello", "created_at": 2}]}

    fake_dify = _FakeDifyClient()

    def _override_get_dify_client():
        return fake_dify

    fastapi_app.dependency_overrides[get_dify_client] = _override_get_dify_client
    fastapi_app.state._test_dify = fake_dify

    yield fastapi_app

    await fake_redis.aclose()
    tmp_dir.cleanup()
