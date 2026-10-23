from __future__ import annotations

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.rate_limit import RateLimitBackend, build_rate_limit_backend

_SKIP_PATHS = frozenset(
    {
        "/",
        "/api/v1/health",
        "/livez",
        "/healthz",
        "/readyz",
        "/api/v1/ops/metrics",
        "/docs",
        "/openapi.json",
        "/redoc",
    }
)

# DENY blocks iframe embedding only; top-level /docs and /redoc still work.
_SECURITY_HEADERS = (
    ("X-Content-Type-Options", "nosniff"),
    ("X-Frame-Options", "DENY"),
    ("Referrer-Policy", "strict-origin-when-cross-origin"),
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach baseline response security headers (toggle via SECURITY_HEADERS_ENABLED)."""

    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        if self.enabled:
            for name, value in _SECURITY_HEADERS:
                response.headers.setdefault(name, value)
        return response


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiter: memory (single-node) or Redis when RATE_LIMIT_BACKEND=redis."""

    def __init__(
        self,
        app,
        requests_per_minute: int = 120,
        backend: RateLimitBackend | None = None,
        backend_name: str = "memory",
        redis_url: str = "",
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.backend = backend or build_rate_limit_backend(backend_name, redis_url)
        self.backend_name = backend_name if backend is None else "injected"

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in _SKIP_PATHS:
            return await call_next(request)
        ip = request.client.host if request.client else "unknown"
        if not self.backend.allow(ip, self.requests_per_minute):
            return JSONResponse(
                {"detail": "Rate limit exceeded"},
                status_code=429,
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "Retry-After": "60",
                },
            )
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        return response
