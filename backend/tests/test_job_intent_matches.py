"""job_intent_matches upsert on ingest (Demand Compass provenance)."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from app.collectors.base import RawJob
from app.ingestion.service import upsert_raw_job
from app.storage.db import SessionLocal
from app.storage.models import JobIntentMatch, SearchQuery, Source


@pytest.fixture()
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def _unique(prefix: str) -> str:
    return f"{prefix}_{datetime.now(timezone.utc).timestamp()}"


def test_upsert_creates_and_updates_intent_match(db):
    source = Source(
        name=_unique("test_match_src"),
        source_type="api",
        connector_type="remotive",
        connector_status="enabled",
        enabled=True,
    )
    db.add(source)
    intent = SearchQuery(
        name=_unique("Match Test"),
        query_text="kubernetes",
        kind="discovery",
        origin="seed_discovery",
        enabled=True,
    )
    db.add(intent)
    db.flush()

    raw = RawJob(
        source_job_id=_unique("j1"),
        url=f"https://example.com/jobs/{_unique('j1-intent-match')}",
        title="Kubernetes Engineer",
        company="Acme",
        description="K8s platform role",
        published_at=datetime.now(timezone.utc),
    )
    job, action = upsert_raw_job(db, source_id=source.id, raw=raw, query_id=intent.id)
    db.flush()
    assert action == "inserted"
    assert job.query_id == intent.id
    match = db.scalar(
        select(JobIntentMatch).where(
            JobIntentMatch.job_id == job.id, JobIntentMatch.query_id == intent.id
        )
    )
    assert match is not None
    first = match.first_matched_at

    job2, action2 = upsert_raw_job(db, source_id=source.id, raw=raw, query_id=intent.id)
    db.flush()
    assert action2 == "updated"
    assert job2.id == job.id
    match2 = db.scalar(
        select(JobIntentMatch).where(
            JobIntentMatch.job_id == job.id, JobIntentMatch.query_id == intent.id
        )
    )
    assert match2 is not None
    assert match2.first_matched_at == first
    assert match2.last_matched_at >= first


def test_second_intent_match_on_update_preserves_first_query_id(db):
    """Dedup update with a new query_id upserts a match but does not overwrite jobs.query_id."""
    source = Source(
        name=_unique("test_match_src2"),
        source_type="api",
        connector_type="remotive",
        connector_status="enabled",
        enabled=True,
    )
    db.add(source)
    first_intent = SearchQuery(
        name=_unique("First Intent"),
        query_text="java",
        kind="focus",
        origin="seed_focus",
        enabled=True,
    )
    second_intent = SearchQuery(
        name=_unique("Second Intent"),
        query_text="python",
        kind="discovery",
        origin="seed_discovery",
        enabled=True,
    )
    db.add(first_intent)
    db.add(second_intent)
    db.flush()

    raw = RawJob(
        source_job_id=_unique("j2"),
        url=f"https://example.com/jobs/{_unique('j2-dual-match')}",
        title="Backend Engineer",
        company="Acme",
        description="Java and Python services",
        published_at=datetime.now(timezone.utc),
    )
    job, action = upsert_raw_job(db, source_id=source.id, raw=raw, query_id=first_intent.id)
    db.flush()
    assert action == "inserted"
    assert job.query_id == first_intent.id

    job2, action2 = upsert_raw_job(db, source_id=source.id, raw=raw, query_id=second_intent.id)
    db.flush()
    assert action2 == "updated"
    assert job2.id == job.id
    assert job2.query_id == first_intent.id  # first-acquiring intent only

    matches = list(
        db.scalars(select(JobIntentMatch).where(JobIntentMatch.job_id == job.id)).all()
    )
    query_ids = {m.query_id for m in matches}
    assert query_ids == {first_intent.id, second_intent.id}
