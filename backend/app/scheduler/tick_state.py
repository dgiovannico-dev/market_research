"""UTC-day idempotency for daily crawlers (Redis preferred, in-memory fallback)."""

from __future__ import annotations

from datetime import date
from typing import Any

import structlog

from app.core.config import get_settings

log = structlog.get_logger()

_KEY_PREFIX = "fmi:daily_crawler:"
_memory: dict[str, bool] = {}
_redis_client: Any = None
_redis_checked = False


def _day_key(day: date) -> str:
    return f"{_KEY_PREFIX}{day.isoformat()}"


def _get_redis() -> Any | None:
    global _redis_client, _redis_checked
    if _redis_checked:
        return _redis_client
    _redis_checked = True
    try:
        import redis

        settings = get_settings()
        client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
        client.ping()
        _redis_client = client
        return _redis_client
    except Exception as exc:  # noqa: BLE001
        log.info("daily_crawler_tick_redis_unavailable", error=str(exc), fallback="memory")
        _redis_client = None
        return None


def already_succeeded(day: date) -> bool:
    key = _day_key(day)
    client = _get_redis()
    if client is not None:
        try:
            return bool(client.get(key))
        except Exception as exc:  # noqa: BLE001
            log.warning("daily_crawler_tick_redis_get_failed", error=str(exc))
    return bool(_memory.get(key))


def mark_succeeded(day: date) -> None:
    key = _day_key(day)
    client = _get_redis()
    if client is not None:
        try:
            # Keep ~36h so late UTC ticks still see yesterday's marker if needed.
            client.setex(key, 36 * 3600, "1")
            return
        except Exception as exc:  # noqa: BLE001
            log.warning("daily_crawler_tick_redis_set_failed", error=str(exc))
    _memory[key] = True


def clear_tick_state(day: date | None = None) -> None:
    """Test helper: clear one day or all in-memory markers (and Redis key if day set)."""
    global _memory
    if day is None:
        _memory = {}
        return
    key = _day_key(day)
    _memory.pop(key, None)
    client = _get_redis()
    if client is not None:
        try:
            client.delete(key)
        except Exception:  # noqa: BLE001
            pass


def reset_redis_probe() -> None:
    """Test helper: force next call to re-probe Redis availability."""
    global _redis_client, _redis_checked
    _redis_client = None
    _redis_checked = False
