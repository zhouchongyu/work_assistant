from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config.settings import settings
import logging


# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,  # 检测断开的连接
    pool_recycle=300,    # 重新连接间隔
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db_session():
    """获取数据库会话的依赖项"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db():
    """初始化数据库连接"""
    try:
        # 尝试连接数据库
        async with engine.begin() as conn:
            logger.info("Database connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()
    logger.info("Database connections closed")