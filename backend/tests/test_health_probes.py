"""Unit tests for liveness / readiness probes (fail path needs no live DB)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.core.health import check_database, check_redis, livez_payload, readyz_payload


def test_livez_payload_is_ok():
    body = livez_payload("1.1.0")
    assert body["status"] == "ok"
    assert body["probe"] == "live"
    assert body["methodology_version"] == "1.1.0"


def test_readyz_ok_when_db_up():
    engine = MagicMock()
    conn = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn
    body, code = readyz_payload(engine, "1.1.0")
    assert code == 200
    assert body["status"] == "ok"
    assert body["database"] == "up"
    assert body["probe"] == "ready"
    assert "redis" not in body


def test_readyz_503_when_db_down():
    engine = MagicMock()
    engine.connect.side_effect = RuntimeError("connection refused")
    body, code = readyz_payload(engine, "1.1.0")
    assert code == 503
    assert body["status"] == "not_ready"
    assert body["database"] == "down"


def test_readyz_requires_redis_when_configured():
    engine = MagicMock()
    conn = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn
    with patch("app.core.health.check_redis", return_value=False):
        body, code = readyz_payload(
            engine,
            "1.1.0",
            redis_url="redis://localhost:6379/0",
            require_redis=True,
        )
    assert code == 503
    assert body["redis"] == "down"
    assert body["database"] == "up"


def test_check_database_false_on_error():
    engine = MagicMock()
    engine.connect.side_effect = OSError("down")
    assert check_database(engine) is False


def test_check_redis_false_on_empty_url():
    assert check_redis("") is False
