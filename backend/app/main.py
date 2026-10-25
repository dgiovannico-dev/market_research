from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.assistant import router as assistant_router
from app.api.v1.market_certs import router as market_certs_router
from app.api.v1.market_extra import router as market_extra_router
from app.api.v1.ops import router as ops_router
from app.api.v1.ops_credentials import router as ops_credentials_router
from app.api.v1.ops_llm import router as ops_llm_router
from app.api.v1.profile_apps import router as profile_apps_router
from app.api.v1.research import router as research_router
from app.api.v1.router import router as v1_router
from app.api.v1.stats import router as stats_router
from app.api.v1.taxonomy import router as taxonomy_router
from app.core.config import get_settings
from app.core.health import livez_payload, readyz_payload
from app.core.logging import setup_logging
from app.core.middleware import SecurityHeadersMiddleware, SimpleRateLimitMiddleware
from app.bootstrap import build_container, reset_container, set_container
from app.scheduler.runner import start_background_scheduler
from app.storage import models  # noqa: F401
from app.storage.db import Base, engine
from app.storage.seed import seed_reference_data


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    container = build_container()
    set_container(container)
    Base.metadata.create_all(bind=container.engine)
    with container.session_scope() as db:
        seed_reference_data(db)
        from app.application.llm.prompts import ensure_seed_prompts

        ensure_seed_prompts(db)
    settings = container.settings
    task = None
    if settings.enable_scheduler:
        task = start_background_scheduler(settings.scheduler_interval_seconds)
    yield
    if task:
        task.cancel()
    reset_container()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Freelance Market Intelligence API",
        version=settings.methodology_version,
        description=(
            "Evidence-first market intelligence for IT freelancers. "
            "Counts reflect observed stored records, not total market size."
        ),
        lifespan=lifespan,
    )
    app.add_middleware(
        SimpleRateLimitMiddleware,
        requests_per_minute=settings.rate_limit_per_minute,
        backend_name=settings.rate_limit_backend,
        redis_url=settings.redis_url,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Outermost: apply security headers on every response (incl. CORS / rate-limit).
    app.add_middleware(
        SecurityHeadersMiddleware,
        enabled=settings.security_headers_enabled,
    )
    app.include_router(v1_router)
    app.include_router(market_extra_router)
    app.include_router(market_certs_router)
    app.include_router(profile_apps_router)
    app.include_router(ops_router)
    app.include_router(ops_credentials_router)
    app.include_router(ops_llm_router)
    app.include_router(research_router)
    app.include_router(assistant_router)
    app.include_router(taxonomy_router)
    app.include_router(stats_router)

    @app.get("/")
    def root() -> dict[str, str]:
        return {"service": "Freelance Market Intelligence", "docs": "/docs"}

    def _live() -> dict[str, str]:
        """Liveness: process up; no dependency checks."""
        return livez_payload(settings.methodology_version)

    def _ready() -> JSONResponse:
        """Readiness: 200 when DB (and Redis if required) is up, else 503."""
        require_redis = settings.rate_limit_backend.strip().lower() == "redis"
        body, code = readyz_payload(
            engine,
            settings.methodology_version,
            redis_url=settings.redis_url,
            require_redis=require_redis,
        )
        return JSONResponse(content=body, status_code=code)

    @app.get("/livez")
    def livez() -> dict[str, str]:
        """Public liveness probe (process up; no dependency checks)."""
        return _live()

    @app.get("/healthz")
    def healthz() -> JSONResponse:
        """Public readiness probe (same as /readyz; kept for existing clients)."""
        return _ready()

    @app.get("/readyz")
    def readyz() -> JSONResponse:
        """Public readiness probe (k8s-style; same handler as /healthz)."""
        return _ready()

    return app


app = create_app()
