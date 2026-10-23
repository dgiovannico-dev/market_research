"""Facets analytics against real SessionLocal (rolled back)."""

from datetime import datetime, timezone

import pytest

from app.analytics.facets import market_facets
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


def _seed(db, *, remote: str, contract: str, suffix: str) -> Job:
    src = Source(
        name=f"facet_src_{suffix}_{datetime.now(timezone.utc).timestamp()}",
        source_type="api",
        connector_type="remotive",
        connector_status="enabled",
        enabled=True,
    )
    db.add(src)
    db.flush()
    job = Job(
        source_id=src.id,
        source_job_id=f"facet_{suffix}",
        canonical_url=f"https://example.com/facet/{suffix}-{datetime.now(timezone.utc).timestamp()}",
        title_original=f"Role {suffix}",
        company_original="Acme",
        country_code="ZZ",
        remote_type=remote,
        contract_type=contract,
        published_at=datetime.now(timezone.utc),
        is_canonical=True,
        evidence_tier="standard",
        status="active_unverified",
    )
    db.add(job)
    db.flush()
    return job


def test_market_facets_buckets(db):
    _seed(db, remote="remote", contract="freelance", suffix="a")
    _seed(db, remote="hybrid", contract="employment", suffix="b")
    _seed(db, remote="remote", contract="freelance", suffix="c")
    out = market_facets(db, days=30, country_code="ZZ", min_evidence="all")
    assert out["sample_size"] == 3
    remote = {b["key"]: b["jobs"] for b in out["facets"]["remote"]}
    assert remote.get("remote") == 2
    assert remote.get("hybrid") == 1
    contract = {b["key"]: b["jobs"] for b in out["facets"]["contract"]}
    assert contract.get("freelance") == 2
    assert contract.get("employment") == 1
    assert out["evidence_kind"] == "derived"
    assert "definition" in out
