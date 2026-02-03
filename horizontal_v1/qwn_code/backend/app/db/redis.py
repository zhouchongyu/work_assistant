import redis.asyncio as redis
from app.core.config.settings import settings
import logging


# 创建Redis连接池
redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    decode_responses=True,  # 自动解码响应
    max_connections=20,     # 最大连接数
    retry_on_timeout=True   # 超时时重试
)

# 创建Redis客户端
redis_client = redis.Redis(connection_pool=redis_pool)


async def get_redis_client():
    """获取Redis客户端"""
    return redis_client


async def init_redis():
    """初始化Redis连接"""
    try:
        # 测试连接
        await redis_client.ping()
        logging.info("Redis connection established successfully")
    except Exception as e:
        logging.error(f"Failed to connect to Redis: {e}")
        raise


async def close_redis():
    """关闭Redis连接"""
    await redis_client.close()
    logging.info("Redis connection closed")