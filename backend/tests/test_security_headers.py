from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.core.middleware import SecurityHeadersMiddleware

_EXPECTED = {
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
    "referrer-policy": "strict-origin-when-cross-origin",
}


def test_security_headers_on_response():
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware, enabled=True)

    @app.get("/ping")
    def ping():
        return {"ok": True}

    client = TestClient(app)
    res = client.get("/ping")
    assert res.status_code == 200
    for name, value in _EXPECTED.items():
        assert res.headers[name] == value


def test_security_headers_can_disable():
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware, enabled=False)

    @app.get("/ping")
    def ping():
        return {"ok": True}

    client = TestClient(app)
    res = client.get("/ping")
    assert res.status_code == 200
    for name in _EXPECTED:
        assert name not in res.headers


def test_security_headers_setdefault_preserves_existing():
    """Middleware must not overwrite headers the route already set."""
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware, enabled=True)

    @app.get("/ping")
    def ping():
        return JSONResponse({"ok": True}, headers={"X-Frame-Options": "SAMEORIGIN"})

    client = TestClient(app)
    res = client.get("/ping")
    assert res.status_code == 200
    assert res.headers["x-frame-options"] == "SAMEORIGIN"
    assert res.headers["x-content-type-options"] == "nosniff"
    assert res.headers["referrer-policy"] == "strict-origin-when-cross-origin"
