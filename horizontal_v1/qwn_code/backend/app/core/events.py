from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
from app.core.config.settings import settings
from app.db.session import init_db, close_db
from app.db.redis import init_redis, close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时的操作
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
    logger = logging.getLogger(__name__)
    logger.info("Starting up Work Assistant API...")

    # 初始化数据库连接
    await init_db()

    # 初始化Redis连接
    await init_redis()

    yield  # 应用运行期间

    # 关闭时的操作
    logger.info("Shutting down Work Assistant API...")

    # 关闭数据库连接
    await close_db()

    # 关闭Redis连接
    await close_redis()