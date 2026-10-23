"""Rate limit backends: in-memory (default) or Redis (multi-replica)."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Protocol

import structlog

log = structlog.get_logger(__name__)


class RateLimitBackend(Protocol):
    def allow(self, client_key: str, limit: int) -> bool: ...


class MemoryRateLimitBackend:
    def __init__(self) -> None:
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, client_key: str, limit: int) -> bool:
        now = time.time()
        window = self.hits[client_key]
        while window and now - window[0] > 60:
            window.popleft()
        if len(window) >= limit:
            return False
        window.append(now)
        return True


class RedisRateLimitBackend:
    """Fixed 60s window via INCR + EXPIRE."""

    def __init__(self, redis_url: str) -> None:
        import redis

        self._client = redis.Redis.from_url(redis_url, decode_responses=True)
        self._client.ping()

    def allow(self, client_key: str, limit: int) -> bool:
        bucket = int(time.time() // 60)
        key = f"fmi:rl:{client_key}:{bucket}"
        count = int(self._client.incr(key))
        if count == 1:
            self._client.expire(key, 70)
        return count <= limit


def build_rate_limit_backend(backend: str, redis_url: str) -> RateLimitBackend:
    name = (backend or "memory").strip().lower()
    if name == "redis":
        try:
            return RedisRateLimitBackend(redis_url)
        except Exception as exc:  # noqa: BLE001
            log.warning("redis_rate_limit_unavailable", error=str(exc), fallback="memory")
            return MemoryRateLimitBackend()
    return MemoryRateLimitBackend()
