from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config.settings import settings
from app.core.events import lifespan
from app.api.v1.api import api_router
from app.core.middlewares import RequestLoggingMiddleware
from app.core.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan_wrapper(app: FastAPI):
    """应用生命周期管理"""
    async with lifespan(app) as manager:
        yield manager


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        lifespan=lifespan_wrapper
    )

    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 添加日志中间件（应该在其他中间件之前）
    app.add_middleware(RequestLoggingMiddleware)

    # 注册异常处理器
    register_exception_handlers(app)

    # 包含 API 路由
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )