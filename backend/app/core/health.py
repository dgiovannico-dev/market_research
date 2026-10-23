"""Public liveness / readiness probes (no API key)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine


def check_database(engine: Engine) -> bool:
    """Return True when Postgres answers SELECT 1."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:  # noqa: BLE001 — probe must never raise
        return False


def check_redis(redis_url: str) -> bool:
    """Return True when Redis answers PING."""
    if not redis_url:
        return False
    try:
        import redis

        client = redis.Redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=2)
        return bool(client.ping())
    except Exception:  # noqa: BLE001 — probe must never raise
        return False


def livez_payload(methodology_version: str) -> dict[str, str]:
    """Process is up; does not touch dependencies."""
    return {
        "status": "ok",
        "service": "fmi-api",
        "probe": "live",
        "methodology_version": methodology_version,
    }


def readyz_payload(
    engine: Engine,
    methodology_version: str,
    *,
    redis_url: str = "",
    require_redis: bool = False,
) -> tuple[dict[str, Any], int]:
    """
    Readiness for traffic: DB must be up; Redis only when required.

    Used by both ``/readyz`` and ``/healthz``. Returns (body, http_status).
    503 when a required dependency is down so load balancers / compose
    healthchecks fail closed (``curl -sf``).
    """
    db_up = check_database(engine)
    redis_status: str | None = None
    redis_ok = True
    if require_redis:
        redis_ok = check_redis(redis_url)
        redis_status = "up" if redis_ok else "down"

    ready = db_up and redis_ok
    body: dict[str, Any] = {
        "status": "ok" if ready else "not_ready",
        "database": "up" if db_up else "down",
        "service": "fmi-api",
        "probe": "ready",
        "methodology_version": methodology_version,
    }
    if redis_status is not None:
        body["redis"] = redis_status
    return body, 200 if ready else 503
