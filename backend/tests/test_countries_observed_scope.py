"""Country comparison table lists observed ISO codes, not FOCUS_COUNTRIES only."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.analytics.countries import country_comparison
from app.storage.db import SessionLocal
from app.storage.models import Job, Source


@pytest.fixture()
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def _source(db, suffix: str) -> Source:
    src = Source(
        name=f"countries_scope_{suffix}_{datetime.now(timezone.utc).timestamp()}",
        source_type="api",
        connector_type="remotive",
        connector_status="enabled",
        enabled=True,
    )
    db.add(src)
    db.flush()
    return src


def _job(db, source: Source, *, slug: str, country: str) -> Job:
    job = Job(
        source_id=source.id,
        source_job_id=slug,
        canonical_url=(
            f"https://example.com/jobs/{slug}-{datetime.now(timezone.utc).timestamp()}"
        ),
        title_original=f"Role {slug}",
        company_original="Acme",
        country_code=country,
        published_at=datetime.now(timezone.utc),
        is_canonical=True,
    )
    db.add(job)
    db.flush()
    return job


def test_unfiltered_includes_non_focus_iso(db):
    src = _source(db, "sg")
    _job(db, src, slug="it1", country="IT")
    _job(db, src, slug="sg1", country="SG")
    db.commit()

    out = country_comparison(db, days=90, lens="market")
    codes = {row["country_code"] for row in out["items"]}
    assert "IT" in codes
    assert "SG" in codes
    assert out.get("countries") is None


def test_country_filter_scopes_to_selected(db):
    src = _source(db, "filt")
    _job(db, src, slug="it2", country="IT")
    _job(db, src, slug="sg2", country="SG")
    db.commit()

    out = country_comparison(db, days=90, lens="market", country_code="SG")
    codes = [row["country_code"] for row in out["items"]]
    assert codes == ["SG"]
    assert out.get("countries") == ["SG"]
