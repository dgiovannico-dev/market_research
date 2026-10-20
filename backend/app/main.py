from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.storage.db import Base, SessionLocal, engine
from app.storage import models  # noqa: F401
from app.storage.seed import seed_reference_data


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_reference_data(db)
    finally:
        db.close()
    yield


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
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(v1_router)

    @app.get("/")
    def root() -> dict[str, str]:
        return {"service": "Freelance Market Intelligence", "docs": "/docs"}

    return app


app = create_app()
