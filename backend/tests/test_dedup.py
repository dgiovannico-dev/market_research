"""Dedup helpers + upsert edge cases for correct job storage."""

from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from sqlalchemy import func, select, text

from app.collectors.base import RawJob
from app.ingestion.service import find_duplicate, ingest_raw_jobs, upsert_raw_job
from app.normalization.hashing import content_hash
from app.normalization.url import canonicalize_url
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


def _unique(prefix: str) -> str:
    return f"{prefix}_{datetime.now(timezone.utc).timestamp()}"


def _source(db, prefix: str = "dedup_src") -> Source:
    source = Source(
        name=_unique(prefix),
        source_type="api",
        connector_type="remotive",
        connector_status="enabled",
        enabled=True,
    )
    db.add(source)
    db.flush()
    return source


def test_url_and_hash_helpers_for_dedup():
    a = canonicalize_url("https://jobs.example/a?utm_campaign=1")
    b = canonicalize_url("https://jobs.example/a")
    assert a == b
    assert content_hash("Same body") == content_hash("same   body")


def test_same_url_different_source_job_id_is_duplicate_not_new_row(db):
    source = _source(db)
    url = f"https://example.com/jobs/{_unique('same-url')}"
    first = RawJob(
        source_job_id=_unique("native-a"),
        url=url,
        title="Engineer A",
        company="Acme",
        description="Role description A",
        published_at=datetime.now(timezone.utc),
    )
    second = RawJob(
        source_job_id=_unique("native-b"),
        url=url,
        title="Engineer B",
        company="Acme",
        description="Role description B refreshed",
        published_at=datetime.now(timezone.utc),
    )

    job1, action1 = upsert_raw_job(db, source_id=source.id, raw=first)
    db.flush()
    assert action1 == "inserted"

    job2, action2 = upsert_raw_job(db, source_id=source.id, raw=second)
    db.flush()
    assert action2 == "duplicate"
    assert job2.id == job1.id
    assert job2.title_original == "Engineer B"

    count = db.scalar(
        select(func.count()).select_from(Job).where(Job.source_id == source.id)
    )
    assert count == 1


def test_same_source_job_id_refreshes_fields_without_new_row(db):
    source = _source(db, "dedup_update")
    sid = _unique("native-same")
    url = f"https://example.com/jobs/{_unique('update-url')}"
    original = RawJob(
        source_job_id=sid,
        url=url,
        title="Original Title",
        company="Acme",
        description="Original description body",
        location="Berlin",
        published_at=datetime.now(timezone.utc),
    )
    refreshed = RawJob(
        source_job_id=sid,
        url=url,
        title="Updated Title",
        company="Acme Corp",
        description="Updated description body with more detail",
        location="Remote DE",
        published_at=datetime.now(timezone.utc),
    )

    job1, action1 = upsert_raw_job(db, source_id=source.id, raw=original)
    db.flush()
    assert action1 == "inserted"
    first_seen = job1.first_seen_at

    job2, action2 = upsert_raw_job(db, source_id=source.id, raw=refreshed)
    db.flush()
    assert action2 == "updated"
    assert job2.id == job1.id
    assert job2.title_original == "Updated Title"
    assert job2.description_original == "Updated description body with more detail"
    assert job2.location_original == "Remote DE"
    assert job2.first_seen_at == first_seen
    assert job2.last_seen_at >= first_seen

    count = db.scalar(
        select(func.count()).select_from(Job).where(Job.source_id == source.id)
    )
    assert count == 1


@pytest.mark.parametrize(
    "blank_url",
    ["", "   ", "\t\n", "/"],
    ids=["empty", "spaces", "whitespace", "path_only"],
)
def test_blank_url_upsert_raises_empty_url(db, blank_url):
    """Blank / non-canonical URLs must raise empty_url — no missing:// fallback."""
    source = _source(db, "dedup_blank_upsert")
    blank = RawJob(
        source_job_id=_unique("no-url"),
        url=blank_url,
        title="No Link Job",
        company="Acme",
        description="Should not persist without a URL",
        published_at=datetime.now(timezone.utc),
    )
    with pytest.raises(ValueError, match="empty_url"):
        upsert_raw_job(db, source_id=source.id, raw=blank)

    count = db.scalar(
        select(func.count()).select_from(Job).where(Job.source_id == source.id)
    )
    assert count == 0


def test_empty_url_is_rejected_and_skipped_by_ingest(db):
    source = _source(db, "dedup_empty_url")
    blank = RawJob(
        source_job_id=_unique("no-url"),
        url="",
        title="No Link Job",
        company="Acme",
        description="Should not persist without a URL",
        published_at=datetime.now(timezone.utc),
    )
    whitespace = RawJob(
        source_job_id=_unique("ws-url"),
        url="   ",
        title="Whitespace URL Job",
        company="Acme",
        description="Whitespace-only URL must also be skipped",
        published_at=datetime.now(timezone.utc),
    )
    valid = RawJob(
        source_job_id=_unique("ok-url"),
        url=f"https://example.com/jobs/{_unique('ok')}",
        title="Valid Job",
        company="Acme",
        description="Persists alongside blank rejects",
        published_at=datetime.now(timezone.utc),
    )

    # ingest_raw_jobs commits; patch commit so the fixture rollback stays effective
    with patch.object(db, "commit"):
        stats = ingest_raw_jobs(
            db, source_id=source.id, raw_jobs=[blank, whitespace, valid]
        )
    assert stats["inserted"] == 1
    assert stats["updated"] == 0
    assert stats["duplicates"] == 0
    assert stats["errors"] == 2

    count = db.scalar(
        select(func.count()).select_from(Job).where(Job.source_id == source.id)
    )
    assert count == 1
    missing = db.scalar(
        select(func.count())
        .select_from(Job)
        .where(
            Job.source_id == source.id,
            Job.canonical_url.like("missing://%"),
        )
    )
    assert missing == 0


def test_same_description_hash_different_urls_stay_separate(db):
    """Multi-location / multi-title ads often share boilerplate — do not merge on hash."""
    source = _source(db, "dedup_hash")
    body = "Identical boilerplate description used in two city postings."
    first = RawJob(
        source_job_id=_unique("hash-a"),
        url=f"https://example.com/jobs/{_unique('city-a')}",
        title="Engineer Berlin",
        company="Acme",
        description=body,
        published_at=datetime.now(timezone.utc),
    )
    second = RawJob(
        source_job_id=_unique("hash-b"),
        url=f"https://example.com/jobs/{_unique('city-b')}",
        title="Engineer Munich",
        company="Acme",
        description=body,
        published_at=datetime.now(timezone.utc),
    )
    job1, action1 = upsert_raw_job(db, source_id=source.id, raw=first)
    db.flush()
    job2, action2 = upsert_raw_job(db, source_id=source.id, raw=second)
    db.flush()
    assert action1 == "inserted"
    assert action2 == "inserted"
    assert job1.id != job2.id
    assert job1.description_hash == job2.description_hash
    count = db.scalar(
        select(func.count()).select_from(Job).where(Job.source_id == source.id)
    )
    assert count == 2


def test_find_duplicate_matches_by_canonical_url(db):

    source = _source(db, "dedup_find")
    url = f"https://example.com/jobs/{_unique('find-url')}"
    raw = RawJob(
        source_job_id=_unique("find-a"),
        url=url,
        title="Find Me",
        company="Acme",
        description="Unique body for find_duplicate",
        published_at=datetime.now(timezone.utc),
    )
    job, _ = upsert_raw_job(db, source_id=source.id, raw=raw)
    db.flush()

    found = find_duplicate(
        db,
        source_id=source.id,
        source_job_id=_unique("other-native"),
        canonical_url=canonicalize_url(url),
        description_hash=None,
    )
    assert found is not None
    assert found.id == job.id


def test_cross_source_same_url_collapses_to_one_row(db):
    a = _source(db, "dedup_src_a")
    b = _source(db, "dedup_src_b")
    url = f"https://example.com/jobs/{_unique('cross-url')}"
    first = RawJob(
        source_job_id=_unique("a-native"),
        url=url,
        title="From A",
        company="Acme",
        description="Shared listing body A",
        published_at=datetime.now(timezone.utc),
    )
    second = RawJob(
        source_job_id=_unique("b-native"),
        url=url + "?utm_source=other",
        title="From B",
        company="Acme",
        description="Shared listing body B",
        published_at=datetime.now(timezone.utc),
    )

    job1, action1 = upsert_raw_job(db, source_id=a.id, raw=first)
    db.flush()
    assert action1 == "inserted"

    job2, action2 = upsert_raw_job(db, source_id=b.id, raw=second)
    db.flush()
    assert action2 == "duplicate"
    assert job2.id == job1.id

    url_count = db.scalar(
        select(func.count())
        .select_from(Job)
        .where(Job.canonical_url == canonicalize_url(url))
    )
    assert url_count == 1


def test_canonical_url_partial_unique_index_exists(db):
    present = db.execute(
        text(
            "SELECT 1 FROM pg_indexes "
            "WHERE tablename = 'jobs' "
            "AND indexname = 'uq_jobs_canonical_url_when_canonical'"
        )
    ).scalar()
    assert present == 1
