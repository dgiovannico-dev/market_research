"""Wave 2: composition root builds without opening a live DB connection."""

from __future__ import annotations

from app.bootstrap import (
    AppContainer,
    build_container,
    get_container,
    reset_container,
    set_container,
)
from app.core.config import get_settings


def test_build_container_has_session_factories():
    reset_container()
    c = build_container(get_settings())
    assert isinstance(c, AppContainer)
    assert callable(c.session_factory)
    assert callable(c.readonly_session_factory)
    assert c.engine is not None
    assert c.settings is not None
    assert hasattr(c.job_write, "ingest_raw_jobs")
    assert hasattr(c.job_write, "soft_expire_source_jobs")
    assert hasattr(c.collectors, "get")
    assert hasattr(c.collectors, "collect")
    assert hasattr(c.source_catalog, "load")
    assert hasattr(c.source_catalog, "summary")
    assert hasattr(c.credentials, "has_credentials")
    assert isinstance(c.source_catalog.summary(), dict)
    assert callable(c.llm_factory)
    assert hasattr(c.llm(), "health")


def test_get_container_singleton_and_reset():
    reset_container()
    a = get_container()
    b = get_container()
    assert a is b
    reset_container()
    c = get_container()
    assert c is not a


def test_set_container_override():
    reset_container()
    custom = build_container(get_settings())
    set_container(custom)
    assert get_container() is custom
    reset_container()


def test_mcp_session_factory_uses_container():
    reset_container()
    from app.mcp import handlers

    factory = handlers._session_factory()
    assert factory is get_container().readonly_session_factory
    reset_container()
