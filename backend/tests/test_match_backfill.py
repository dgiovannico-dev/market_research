"""Corpus rematch for job_intent_matches (dump → focus lens)."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from app.research.match_backfill import (
    backfill_intent_matches,
    clause_matches,
    query_matches_text,
    tokenize_query_clauses,
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


def test_tokenize_or_and_role_fillers():
    assert tokenize_query_clauses("java OR spring boot") == [["java"], ["spring", "boot"]]
    assert query_matches_text("we need a java backend", "Senior Java Contractor")
    assert query_matches_text("kubernetes platform", "Kubernetes Consultant")
    assert not query_matches_text("gardening helper", "Senior Java Contractor")
    assert clause_matches("rag llm engineer", ["rag"])
    assert query_matches_text("build rag pipelines", "RAG Engineer")
    # Short token must be word-bounded (avoid paragraph → rag).
    assert not query_matches_text("write a paragraph about cats", "RAG Engineer")
    # Ambiguous "AI" alone needs a role filler from the query.
    assert query_matches_text("AI engineer for agents", "AI Engineer B2B")
    assert not query_matches_text("retail AI chatbot for support", "AI Engineer B2B")


def test_backfill_creates_focus_matches(db):
    src = Source(
        name=f"bf_src_{datetime.now(timezone.utc).timestamp()}",
        source_type="api",
        connector_type="remotive",
        connector_status="enabled",
        enabled=True,
    )
    db.add(src)
    db.flush()
    intent = SearchQuery(
        name=f"bf_focus_{datetime.now(timezone.utc).timestamp()}",
        query_text="Kubernetes Consultant",
        kind="focus",
        origin="seed_focus",
        enabled=True,
    )
    db.add(intent)
    db.flush()
    job = Job(
        source_id=src.id,
        source_job_id=f"bf_{datetime.now(timezone.utc).timestamp()}",
        canonical_url=f"https://example.com/bf-{datetime.now(timezone.utc).timestamp()}",
        title_original="Platform Engineer",
        description_original="Own our Kubernetes clusters and GitOps",
        company_original="Acme",
        is_canonical=True,
        published_at=datetime.now(timezone.utc),
    )
    db.add(job)
    db.flush()

    result = backfill_intent_matches(
        db, kind="focus", query_ids=[intent.id], enabled_only=True
    )
    assert result["matches_created"] >= 1
    match = db.scalar(
        select(JobIntentMatch).where(
            JobIntentMatch.job_id == job.id, JobIntentMatch.query_id == intent.id
        )
    )
    assert match is not None
