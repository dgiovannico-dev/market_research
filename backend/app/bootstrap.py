"""Shared composition root for web, MCP, scheduler, and scripts (ADR-008 Wave 2).

Drivers resolve infra through ``get_container()`` instead of each opening
``SessionLocal`` / engines ad hoc. Keep this module thin — use cases live under
``app.application``.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Callable, Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.application.ports.driven.collector_gateway import CollectorGateway
from app.application.ports.driven.connector_credentials import ConnectorCredentialsPort
from app.application.ports.driven.external_stats import ExternalStatsGateway
from app.application.ports.driven.job_write import JobWritePort
from app.application.ports.driven.llm_gateway import LlmGateway
from app.application.ports.driven.source_catalog import SourceCatalogPort
from app.core.config import Settings, get_settings

SessionFactory = Callable[[], Session]
LlmFactory = Callable[[], LlmGateway]


@dataclass(frozen=True)
class AppContainer:
    """Process-wide wiring. Prefer ``session_scope`` over bare ``open_session``."""

    settings: Settings
    engine: Engine
    session_factory: SessionFactory
    readonly_session_factory: SessionFactory
    job_write: JobWritePort
    collectors: CollectorGateway
    source_catalog: SourceCatalogPort
    credentials: ConnectorCredentialsPort
    llm_factory: LlmFactory
    external_stats: ExternalStatsGateway

    def open_session(self) -> Session:
        return self.session_factory()

    def open_readonly_session(self) -> Session:
        return self.readonly_session_factory()

    def llm(self) -> LlmGateway:
        return self.llm_factory()

    @contextmanager
    def session_scope(self) -> Iterator[Session]:
        db = self.open_session()
        try:
            yield db
        finally:
            db.close()

    @contextmanager
    def readonly_session_scope(self) -> Iterator[Session]:
        db = self.open_readonly_session()
        try:
            yield db
        finally:
            db.close()


_container: AppContainer | None = None
_readonly_engine: Engine | None = None


def build_container(settings: Settings | None = None) -> AppContainer:
    """Build a fresh container (does not install it as the process singleton)."""
    from app.adapters.driven.catalog import DEFAULT_SOURCE_CATALOG
    from app.adapters.driven.collectors.registry_gateway import RegistryCollectorGateway
    from app.adapters.driven.credentials import DEFAULT_CONNECTOR_CREDENTIALS
    from app.adapters.driven.llm.provider import get_llm_provider
    from app.adapters.driven.persistence.sqlalchemy_job_write import (
        SqlAlchemyJobWriteAdapter,
    )
    from app.adapters.driven.stats import DEFAULT_EXTERNAL_STATS
    from app.storage.db import SessionLocal, engine

    cfg = settings or get_settings()
    readonly = _build_readonly_factory(cfg, fallback=SessionLocal)
    return AppContainer(
        settings=cfg,
        engine=engine,
        session_factory=SessionLocal,
        readonly_session_factory=readonly,
        job_write=SqlAlchemyJobWriteAdapter(),
        collectors=RegistryCollectorGateway(),
        source_catalog=DEFAULT_SOURCE_CATALOG,
        credentials=DEFAULT_CONNECTOR_CREDENTIALS,
        llm_factory=get_llm_provider,
        external_stats=DEFAULT_EXTERNAL_STATS,
    )


def _build_readonly_factory(cfg: Settings, *, fallback: SessionFactory) -> SessionFactory:
    global _readonly_engine
    url = (cfg.database_url_readonly or "").strip()
    if not url:
        return fallback
    if _readonly_engine is None or str(_readonly_engine.url) != url:
        _readonly_engine = create_engine(url, pool_pre_ping=True)
    return sessionmaker(bind=_readonly_engine, autocommit=False, autoflush=False)


def get_container() -> AppContainer:
    """Lazy singleton — safe for scripts/tests that skip FastAPI lifespan."""
    global _container
    if _container is None:
        _container = build_container()
    return _container


def set_container(container: AppContainer | None) -> None:
    global _container
    _container = container


def reset_container() -> None:
    """Clear singleton (tests). Does not dispose engines."""
    set_container(None)
