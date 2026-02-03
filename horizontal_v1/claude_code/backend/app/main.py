"""
FastAPI Application Entry Point.

This is the main entry point for the Work Assistant V2 backend.

Reference:
- assistant_py/main.py: Original FastAPI + RabbitMQ setup
- Wiki: 系统架构/系统架构.md
- Wiki: 后端服务/Python后端服务/Python后端服务.md
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as api_v1_router
from app.core.config import settings
from app.core.database import close_db, init_db
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.redis import close_redis, init_redis, redis_client
from app.middleware.authority import AuthorityMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.request_id import RequestIdMiddleware
from app.workers.rabbitmq import router as rabbitmq_router
from app.mqtt import get_mqtt_client
from app.services.task import task_scheduler

logger = logging.getLogger("work_assistant")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events:
    - Startup: Initialize database, Redis, RabbitMQ, MQTT
    - Shutdown: Close all connections gracefully
    """
    # Startup
    logger.info(
        f"Starting {settings.app_name} v{settings.app_version} "
        f"in {settings.environment} mode"
    )

    # Setup logging
    setup_logging()

    # Initialize database
    logger.info("Initializing database connection...")
    # Note: Table creation is handled by Alembic migrations
    # await init_db()  # Uncomment if you want to create tables on startup

    # Initialize Redis connection
    logger.info("Initializing Redis connection...")
    await init_redis()

    # Initialize MQTT client
    logger.info("Initializing MQTT client...")
    try:
        mqtt_client = get_mqtt_client()
        logger.info("MQTT client initialized")
    except Exception as e:
        logger.warning(f"MQTT client initialization failed (non-critical): {e}")

    # Note: RabbitMQ consumers are initialized via the router include

    # Initialize task scheduler
    logger.info("Initializing task scheduler...")
    try:
        await task_scheduler.start()
        logger.info("Task scheduler initialized")
    except Exception as e:
        logger.warning(f"Task scheduler initialization failed (non-critical): {e}")

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application...")

    # Close Redis connection
    await close_redis()

    # Close database connections
    await close_db()

    # Close MQTT client
    try:
        mqtt_client = get_mqtt_client()
        mqtt_client.close()
        logger.info("MQTT client closed")
    except Exception as e:
        logger.warning(f"MQTT client close failed: {e}")

    # Shutdown task scheduler
    try:
        await task_scheduler.shutdown()
        logger.info("Task scheduler stopped")
    except Exception as e:
        logger.warning(f"Task scheduler shutdown failed: {e}")

    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Work Assistant V2 - Unified Backend API",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    # Register exception handlers
    register_exception_handlers(app)

    # Add middlewares (order matters - first added is outermost)
    # 1. Request ID middleware (outermost)
    app.add_middleware(RequestIdMiddleware)

    # 2. Logging middleware
    app.add_middleware(LoggingMiddleware)

    # 3. Authority middleware (JWT validation and permission checking)
    app.add_middleware(AuthorityMiddleware)

    # 4. CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # Register API routers
    app.include_router(api_v1_router, prefix=settings.api_v1_prefix)

    # Register RabbitMQ router (for faststream consumers)
    app.include_router(rabbitmq_router)

    # Health check endpoint
    @app.get("/health")
    async def health_check() -> dict:
        """Health check endpoint."""
        # Check Redis connection
        redis_healthy = await redis_client.ping()

        return {
            "status": "healthy" if redis_healthy else "degraded",
            "app": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "services": {
                "redis": "healthy" if redis_healthy else "unhealthy",
            },
        }

    # Root endpoint
    @app.get("/")
    async def root() -> dict:
        """Root endpoint."""
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "docs": "/docs" if settings.debug else None,
        }

    return app


# Create application instance
app = create_app()


def main() -> None:
    """Run the application using uvicorn."""
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )


if __name__ == "__main__":
    main()
