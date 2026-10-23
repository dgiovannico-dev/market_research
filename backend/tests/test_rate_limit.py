from app.core.middleware import SimpleRateLimitMiddleware
from app.core.rate_limit import MemoryRateLimitBackend, build_rate_limit_backend
from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_memory_backend_blocks_after_limit():
    backend = MemoryRateLimitBackend()
    assert backend.allow("a", 2) is True
    assert backend.allow("a", 2) is True
    assert backend.allow("a", 2) is False


def test_build_backend_memory_default():
    b = build_rate_limit_backend("memory", "redis://localhost:6379/0")
    assert isinstance(b, MemoryRateLimitBackend)


def test_middleware_returns_429():
    app = FastAPI()
    backend = MemoryRateLimitBackend()
    app.add_middleware(
        SimpleRateLimitMiddleware,
        requests_per_minute=2,
        backend=backend,
    )

    @app.get("/api/v1/ping")
    def ping():
        return {"ok": True}

    client = TestClient(app)
    assert client.get("/api/v1/ping").status_code == 200
    assert client.get("/api/v1/ping").status_code == 200
    blocked = client.get("/api/v1/ping")
    assert blocked.status_code == 429
    assert blocked.json()["detail"] == "Rate limit exceeded"


def test_health_exempt_from_limit():
    app = FastAPI()
    app.add_middleware(
        SimpleRateLimitMiddleware,
        requests_per_minute=1,
        backend=MemoryRateLimitBackend(),
    )

    @app.get("/api/v1/health")
    def health():
        return {"status": "ok"}

    @app.get("/api/v1/ping")
    def ping():
        return {"ok": True}

    client = TestClient(app)
    assert client.get("/api/v1/health").status_code == 200
    assert client.get("/api/v1/health").status_code == 200
    assert client.get("/api/v1/ping").status_code == 200
    assert client.get("/api/v1/ping").status_code == 429
