"""Language demand analytics against real SessionLocal (rolled back)."""

from datetime import datetime, timezone

import pytest

from app.analytics.languages import language_demand
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


def _seed(db, *, langs: list[str], suffix: str) -> Job:
    src = Source(
        name=f"lang_src_{suffix}_{datetime.now(timezone.utc).timestamp()}",
        source_type="api",
        connector_type="remotive",
        connector_status="enabled",
        enabled=True,
    )
    db.add(src)
    db.flush()
    job = Job(
        source_id=src.id,
        source_job_id=f"lang_{suffix}",
        canonical_url=f"https://example.com/lang/{suffix}-{datetime.now(timezone.utc).timestamp()}",
        title_original=f"Role {suffix}",
        company_original="Acme",
        country_code="YY",
        language_requirements=langs,
        published_at=datetime.now(timezone.utc),
        is_canonical=True,
        evidence_tier="standard",
        status="active_unverified",
    )
    db.add(job)
    db.flush()
    return job


def test_language_demand_counts(db):
    _seed(db, langs=["en", "it"], suffix="a")
    _seed(db, langs=["en"], suffix="b")
    _seed(db, langs=[], suffix="c")
    out = language_demand(db, days=90, country_code="YY", min_evidence="all")
    assert out["sample_size"] == 3
    assert out["jobs_with_language_requirements"] == 2
    by_lang = {i["language"]: i["jobs"] for i in out["items"]}
    assert by_lang["en"] == 2
    assert by_lang["it"] == 1
    assert out["coverage_pct"] == round(2 / 3, 4)
