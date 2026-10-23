"""Focus intent text rematch helper (historical job_intent_matches backfill)."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import func, select

from app.research.rematch import (
    job_search_text,
    query_signal_tokens,
    rematch_focus_intents,
    tokens_match_haystack,
)
from app.storage.db import SessionLocal
from app.storage.models import Job, JobIntentMatch, SearchQuery, Source


@pytest.fixture()
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def test_query_signal_tokens_drops_weak_modifiers():
    assert query_signal_tokens("Senior Java Contractor") == ["java"]
    assert query_signal_tokens("Java Spring Boot B2B") == ["java", "spring", "boot"]
    assert query_signal_tokens("RAG Engineer") == ["rag"]


def test_tokens_match_haystack_word_boundaries():
    assert tokens_match_haystack(["rag"], "RAG Engineer for LLMs")
    assert not tokens_match_haystack(["rag"], "average storage role")
    assert tokens_match_haystack(["java", "spring"], "Java Spring Boot services")
    assert not tokens_match_haystack(["java", "spring"], "Java only role")


def test_rematch_focus_intents_creates_idempotent_matches(db):
    src = Source(
        name=f"rematch_src_{datetime.now(timezone.utc).timestamp()}",
        source_type="api",
        connector_type="remotive",
        connector_status="enabled",
        enabled=True,
    )
    db.add(src)
    intent = SearchQuery(
        name=f"K8s Focus {datetime.now(timezone.utc).timestamp()}",
        query_text="Kubernetes Consultant",
        kind="focus",
        origin="seed_focus",
        enabled=True,
    )
    other = SearchQuery(
        name=f"Java Focus {datetime.now(timezone.utc).timestamp()}",
        query_text="Senior Java Contractor",
        kind="focus",
        origin="seed_focus",
        enabled=True,
    )
    db.add(intent)
    db.add(other)
    db.flush()

    hit = Job(
        source_id=src.id,
        source_job_id=f"k8s_{datetime.now(timezone.utc).timestamp()}",
        canonical_url=f"https://example.com/jobs/k8s-{datetime.now(timezone.utc).timestamp()}",
        title_original="Platform Engineer Kubernetes",
        description_original="Operate clusters",
        country_code="DE",
        published_at=datetime.now(timezone.utc),
        is_canonical=True,
    )
    miss = Job(
        source_id=src.id,
        source_job_id=f"mkt_{datetime.now(timezone.utc).timestamp()}",
        canonical_url=f"https://example.com/jobs/mkt-{datetime.now(timezone.utc).timestamp()}",
        title_original="Marketing Manager",
        description_original="Brand campaigns",
        country_code="US",
        published_at=datetime.now(timezone.utc),
        is_canonical=True,
    )
    db.add(hit)
    db.add(miss)
    db.flush()

    hay = job_search_text(hit)
    assert tokens_match_haystack(query_signal_tokens(intent.query_text), hay)

    stats = rematch_focus_intents(db, query_ids=[intent.id, other.id], dry_run=False)
    assert stats["candidates"] >= 1
    assert stats["created"] >= 1

    match = db.scalar(
        select(JobIntentMatch).where(
            JobIntentMatch.job_id == hit.id, JobIntentMatch.query_id == intent.id
        )
    )
    assert match is not None
    first = match.first_matched_at

    stats2 = rematch_focus_intents(db, query_ids=[intent.id], dry_run=False)
    assert stats2["created"] == 0
    assert stats2["updated"] >= 1
    match2 = db.scalar(
        select(JobIntentMatch).where(
            JobIntentMatch.job_id == hit.id, JobIntentMatch.query_id == intent.id
        )
    )
    assert match2 is not None
    assert match2.first_matched_at == first

    no_java = db.scalar(
        select(JobIntentMatch).where(
            JobIntentMatch.job_id == hit.id, JobIntentMatch.query_id == other.id
        )
    )
    assert no_java is None


def test_rematch_focus_intents_dry_run_writes_nothing(db):
    src = Source(
        name=f"rematch_dry_{datetime.now(timezone.utc).timestamp()}",
        source_type="api",
        connector_type="remotive",
        connector_status="enabled",
        enabled=True,
    )
    db.add(src)
    intent = SearchQuery(
        name=f"RAG dry {datetime.now(timezone.utc).timestamp()}",
        query_text="RAG Engineer",
        kind="focus",
        origin="seed_focus",
        enabled=True,
    )
    db.add(intent)
    db.flush()
    job = Job(
        source_id=src.id,
        source_job_id=f"rag_{datetime.now(timezone.utc).timestamp()}",
        canonical_url=f"https://example.com/jobs/rag-{datetime.now(timezone.utc).timestamp()}",
        title_original="RAG Engineer",
        description_original="Retrieval augmented generation",
        country_code="CH",
        published_at=datetime.now(timezone.utc),
        is_canonical=True,
    )
    db.add(job)
    db.flush()

    before = db.scalar(
        select(func.count())
        .select_from(JobIntentMatch)
        .where(JobIntentMatch.query_id == intent.id)
    )
    stats = rematch_focus_intents(db, query_ids=[intent.id], dry_run=True)
    after = db.scalar(
        select(func.count())
        .select_from(JobIntentMatch)
        .where(JobIntentMatch.query_id == intent.id)
    )

    assert stats["dry_run"] is True
    assert stats["candidates"] >= 1
    assert stats["created"] == 0
    assert stats["updated"] == 0
    assert stats["skipped"] == stats["candidates"]
    assert after == before
