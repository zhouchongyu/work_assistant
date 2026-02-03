"""
Async Redis client and utilities.

Provides:
- Async Redis connection management
- Distributed locking
- Caching utilities with TTL
- Idempotency key management

Reference:
- assistant_py/db/syncRedis.py: Original sync Redis client
- Wiki: 数据管理/缓存与存储.md
"""

import json
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import redis.asyncio as aioredis
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.middleware.request_id import get_request_id

logger = logging.getLogger("work_assistant.redis")


class RedisClient:
    """
    Async Redis client with connection pooling.

    Features:
    - Automatic reconnection
    - Connection pooling
    - Health checks
    """

    _instance: "RedisClient | None" = None
    _pool: aioredis.ConnectionPool | None = None
    _client: Redis | None = None

    def __new__(cls) -> "RedisClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self) -> None:
        """Initialize Redis connection pool."""
        if self._pool is not None:
            return

        self._pool = aioredis.ConnectionPool.from_url(
            settings.redis.url,
            max_connections=20,
            decode_responses=True,
            health_check_interval=30,
        )
        self._client = Redis(connection_pool=self._pool)
        logger.info("Redis connection pool initialized")

    async def disconnect(self) -> None:
        """Close Redis connection pool."""
        if self._client:
            await self._client.aclose()
            self._client = None
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
        logger.info("Redis connection pool closed")

    @property
    def client(self) -> Redis:
        """Get the Redis client instance."""
        if self._client is None:
            raise RuntimeError("Redis client not initialized. Call connect() first.")
        return self._client

    async def ping(self) -> bool:
        """Check Redis connection health."""
        try:
            return await self.client.ping()
        except RedisError as e:
            logger.error(f"Redis ping failed: {e}")
            return False


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> Redis:
    """Get the Redis client instance."""
    return redis_client.client


@asynccontextmanager
async def get_redis_context() -> AsyncGenerator[Redis, None]:
    """Context manager for Redis operations with error handling."""
    try:
        yield redis_client.client
    except RedisError as e:
        logger.error(f"Redis error: {e}", extra={"request_id": get_request_id()})
        raise


class DistributedLock:
    """
    Distributed lock using Redis.

    Usage:
        async with DistributedLock("consumer_extract:123", expire=60) as acquired:
            if acquired:
                # Do work
                pass
            else:
                # Lock not acquired
                pass

    Key format: lock:{key}
    Value: request_id (for debugging)
    """

    KEY_PREFIX = "lock:"

    def __init__(
        self,
        key: str,
        expire: int = 30,
        auto_release: bool = True,
    ) -> None:
        """
        Initialize distributed lock.

        Args:
            key: Lock key (without prefix)
            expire: Lock expiration in seconds (default: 30)
            auto_release: Whether to auto-release on exit (default: True)
        """
        self.key = f"{self.KEY_PREFIX}{key}"
        self.expire = expire
        self.auto_release = auto_release
        self._acquired = False
        self._value = get_request_id() or "unknown"

    async def acquire(self) -> bool:
        """
        Attempt to acquire the lock.

        Returns:
            True if lock was acquired, False otherwise
        """
        try:
            result = await redis_client.client.set(
                self.key,
                self._value,
                nx=True,
                ex=self.expire,
            )
            self._acquired = result is True
            if self._acquired:
                logger.debug(f"Lock acquired: {self.key}")
            else:
                logger.debug(f"Lock not acquired (already held): {self.key}")
            return self._acquired
        except RedisError as e:
            # Fail-open: if Redis is down, allow operation but log warning
            logger.warning(f"Redis lock failed, degrading: {e}")
            self._acquired = True  # Degrade to allow operation
            return True

    async def release(self) -> bool:
        """
        Release the lock.

        Returns:
            True if lock was released, False if not held
        """
        if not self._acquired:
            return False

        try:
            # Only release if we still hold the lock (compare value)
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            result = await redis_client.client.eval(
                lua_script, 1, self.key, self._value
            )
            if result:
                logger.debug(f"Lock released: {self.key}")
            self._acquired = False
            return bool(result)
        except RedisError as e:
            logger.warning(f"Failed to release lock {self.key}: {e}")
            self._acquired = False
            return False

    async def __aenter__(self) -> bool:
        """Async context manager entry."""
        return await self.acquire()

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self.auto_release:
            await self.release()


class IdempotencyManager:
    """
    Idempotency key manager using Redis.

    Used to prevent duplicate processing of messages/requests.

    Key format: idem:{type}:{id}:{version}
    TTL: 7 days (default)
    """

    KEY_PREFIX = "idem:"
    DEFAULT_TTL = 60 * 60 * 24 * 7  # 7 days

    @classmethod
    async def check_and_set(
        cls,
        key_type: str,
        entity_id: int | str,
        version: int | str,
        ttl: int | None = None,
    ) -> bool:
        """
        Check if operation was already processed and mark as processed.

        Args:
            key_type: Type of operation (e.g., "extract", "compare")
            entity_id: Entity ID
            version: Entity version
            ttl: TTL in seconds (default: 7 days)

        Returns:
            True if this is a new operation (not processed before)
            False if already processed (duplicate)
        """
        key = f"{cls.KEY_PREFIX}{key_type}:{entity_id}:{version}"
        ttl = ttl or cls.DEFAULT_TTL

        try:
            # SET NX returns True if key was set (new operation)
            result = await redis_client.client.set(key, "1", nx=True, ex=ttl)
            if result:
                logger.debug(f"Idempotency key set: {key}")
                return True
            else:
                logger.debug(f"Duplicate operation detected: {key}")
                return False
        except RedisError as e:
            # Fail-open for idempotency (allow operation but log)
            logger.warning(f"Redis idempotency check failed, allowing: {e}")
            return True

    @classmethod
    async def check(
        cls,
        key_type: str,
        entity_id: int | str,
        version: int | str,
    ) -> bool:
        """
        Check if operation was already processed (without setting).

        Returns:
            True if already processed
            False if not processed
        """
        key = f"{cls.KEY_PREFIX}{key_type}:{entity_id}:{version}"

        try:
            result = await redis_client.client.exists(key)
            return bool(result)
        except RedisError as e:
            logger.warning(f"Redis idempotency check failed: {e}")
            return False


class CacheManager:
    """
    Cache manager with TTL support.

    Key format: cache:{namespace}:{key}
    """

    KEY_PREFIX = "cache:"

    @classmethod
    async def get(
        cls,
        namespace: str,
        key: str,
    ) -> Any | None:
        """
        Get cached value.

        Args:
            namespace: Cache namespace (e.g., "dict", "menu")
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        cache_key = f"{cls.KEY_PREFIX}{namespace}:{key}"

        try:
            value = await redis_client.client.get(cache_key)
            if value:
                return json.loads(value)
            return None
        except (RedisError, json.JSONDecodeError) as e:
            logger.warning(f"Cache get failed for {cache_key}: {e}")
            return None

    @classmethod
    async def set(
        cls,
        namespace: str,
        key: str,
        value: Any,
        ttl: int = 1800,  # 30 minutes default
    ) -> bool:
        """
        Set cached value.

        Args:
            namespace: Cache namespace
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: TTL in seconds (default: 30 minutes)

        Returns:
            True if successful
        """
        cache_key = f"{cls.KEY_PREFIX}{namespace}:{key}"

        try:
            await redis_client.client.set(
                cache_key,
                json.dumps(value, ensure_ascii=False),
                ex=ttl,
            )
            return True
        except (RedisError, TypeError) as e:
            logger.warning(f"Cache set failed for {cache_key}: {e}")
            return False

    @classmethod
    async def delete(
        cls,
        namespace: str,
        key: str,
    ) -> bool:
        """Delete cached value."""
        cache_key = f"{cls.KEY_PREFIX}{namespace}:{key}"

        try:
            await redis_client.client.delete(cache_key)
            return True
        except RedisError as e:
            logger.warning(f"Cache delete failed for {cache_key}: {e}")
            return False

    @classmethod
    async def invalidate_namespace(cls, namespace: str) -> int:
        """
        Invalidate all keys in a namespace.

        Returns:
            Number of keys deleted
        """
        pattern = f"{cls.KEY_PREFIX}{namespace}:*"

        try:
            keys = []
            async for key in redis_client.client.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                return await redis_client.client.delete(*keys)
            return 0
        except RedisError as e:
            logger.warning(f"Cache invalidate failed for {pattern}: {e}")
            return 0


class CounterManager:
    """
    Counter manager for rate limiting and metrics.

    Key format: counter:{namespace}:{key}
    """

    KEY_PREFIX = "counter:"

    @classmethod
    async def incr(
        cls,
        namespace: str,
        key: str,
        ttl: int = 3600,  # 1 hour default
    ) -> int:
        """
        Increment counter and return new value.

        Args:
            namespace: Counter namespace
            key: Counter key
            ttl: TTL in seconds (default: 1 hour)

        Returns:
            New counter value
        """
        counter_key = f"{cls.KEY_PREFIX}{namespace}:{key}"

        try:
            pipe = redis_client.client.pipeline()
            pipe.incr(counter_key)
            pipe.expire(counter_key, ttl)
            results = await pipe.execute()
            return results[0]
        except RedisError as e:
            logger.warning(f"Counter incr failed for {counter_key}: {e}")
            return 0

    @classmethod
    async def get(cls, namespace: str, key: str) -> int:
        """Get current counter value."""
        counter_key = f"{cls.KEY_PREFIX}{namespace}:{key}"

        try:
            value = await redis_client.client.get(counter_key)
            return int(value) if value else 0
        except (RedisError, ValueError) as e:
            logger.warning(f"Counter get failed for {counter_key}: {e}")
            return 0


# Initialization and shutdown helpers
async def init_redis() -> None:
    """Initialize Redis connection."""
    await redis_client.connect()


async def close_redis() -> None:
    """Close Redis connection."""
    await redis_client.disconnect()
