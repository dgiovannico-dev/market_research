"""Wave 5b–6: catalog/credentials ports + research intent policies / lens scope."""

from __future__ import annotations

from unittest.mock import MagicMock

from sqlalchemy import select

from app.adapters.driven.catalog import JsonFileSourceCatalog
from app.adapters.driven.credentials import SettingsConnectorCredentials
from app.analytics.lenses import apply_lens_filter
from app.bootstrap import build_container, reset_container
from app.core.config import get_settings
from app.domain.research_intent.policies import (
    apply_soft_delete,
    bump_version,
    resolve_display_name,
)
from app.research.jobs_search import apply_research_job_scope
from app.storage.models import Job


def test_source_catalog_port_loads_summary():
    catalog = JsonFileSourceCatalog()
    data = catalog.load()
    assert "sources" in data
    summary = catalog.summary()
    assert "active_connector_keys" in summary or "by_status" in summary or summary


def test_credentials_port_delegates():
    port = SettingsConnectorCredentials()
    # Free ACTIVE connectors typically need no secrets.
    assert isinstance(port.has_credentials("remotive"), bool)


def test_container_exposes_catalog_and_credentials():
    reset_container()
    c = build_container(get_settings())
    assert c.source_catalog.summary()
    assert isinstance(c.credentials.has_credentials("remotive"), bool)
    reset_container()


def test_resolve_display_name_and_soft_delete_policies():
    assert resolve_display_name(name="  A  ") == "A"
    assert resolve_display_name(label="B") == "B"
    try:
        resolve_display_name()
        raise AssertionError("expected ValueError")
    except ValueError:
        pass

    row = MagicMock(version=1, enabled=True, deleted_at=None)
    bump_version(row)
    assert row.version == 2
    apply_soft_delete(row)
    assert row.enabled is False
    assert row.deleted_at is not None


def test_research_scope_delegates_lens_to_analytics():
    """Explore lens path must use the same filter as market analytics."""
    db = MagicMock()
    stmt = select(Job)
    scoped = apply_research_job_scope(db, stmt, lens="market")
    via_lens = apply_lens_filter(stmt, db, lens="market")
    assert str(scoped) == str(via_lens)
