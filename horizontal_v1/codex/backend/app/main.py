from fastapi import FastAPI

from backend.app.api.v1.router import router as v1_router
from backend.app.core.exceptions import register_exception_handlers
from backend.app.core.request_id import request_id_middleware
from backend.app.core.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="work-assistant-v3")
    app.state.settings = settings
    app.middleware("http")(request_id_middleware)
    register_exception_handlers(app)
    app.include_router(v1_router, prefix="/api/v1")
    return app
