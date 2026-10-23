"""Ingest must clip long employment_type and isolate row failures with savepoints."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.collectors.base import RawJob
from app.ingestion.service import _apply_remote_hint, _clip, ingest_raw_jobs
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


def test_clip_employment_type():
    long = "x" * 80
    assert len(_clip(long, 64) or "") == 64
    assert _clip("short", 64) == "short"
    assert _clip(None, 64) is None


def test_apply_remote_hint_strings():
    assert _apply_remote_hint("unknown", "hybrid") == "hybrid"
    assert _apply_remote_hint("unknown", True) == "remote"
    assert _apply_remote_hint("remote", "onsite") == "remote"


def test_ingest_clips_long_job_type(db):
    source = Source(
        name=f"clip-emp-{datetime.now(timezone.utc).timestamp()}",
        source_type="api",
        connector_type="test",
        enabled=True,
        connector_status="enabled",
    )
    db.add(source)
    db.flush()

    long_types = (
        "Permanent employment (unbefristeter arbeitsvertrag),"
        "professional / experienced"
    )
    assert len(long_types) > 64
    sid = f"slug-long-emp-{datetime.now(timezone.utc).timestamp()}"

    stats = ingest_raw_jobs(
        db,
        source_id=source.id,
        raw_jobs=[
            RawJob(
                source_job_id=sid,
                url=f"https://example.com/jobs/{sid}",
                title="Mechatronics Engineer",
                company="Acme",
                description="Install automation.",
                location="Berlin",
                published_at=datetime.now(timezone.utc),
                job_type=long_types,
                remote_hint=False,
            )
        ],
        collection_method="api",
    )
    assert stats["errors"] == 0
    assert stats["inserted"] == 1
    job = db.query(Job).filter_by(source_job_id=sid).one()
    assert job.employment_type is not None
    assert len(job.employment_type) <= 64
