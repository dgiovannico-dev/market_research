"""Soft-expire + job_query default corpus filters."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from sqlalchemy.dialects import postgresql

from app.analytics.job_query import base_job_query
from app.ingestion.soft_expire import STALE_AFTER_DAYS, soft_expire_source_jobs


def _compile(stmt) -> str:
    return str(
        stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": False})
    )


def test_base_job_query_excludes_closed_by_default():
    sql = _compile(base_job_query())
    assert "is_canonical" in sql
    assert "closed_stale" in sql or "NOT IN" in sql.upper() or "notin" in sql.lower()


def test_base_job_query_include_closed_skips_status_filter():
    with_closed = _compile(base_job_query(include_closed=True))
    without = _compile(base_job_query(include_closed=False))
    assert "status" in without.lower()
    # include_closed should not add the NOT IN status clause (fewer binds)
    assert with_closed.count("status") <= without.count("status")


def test_base_job_query_min_evidence_standard():
    sql = _compile(base_job_query(min_evidence="standard"))
    assert "evidence_tier" in sql


def test_soft_expire_age_only_when_dump_incomplete():
    db = MagicMock()
    result = MagicMock()
    result.rowcount = 3
    db.execute.return_value = result
    seen = datetime.now(timezone.utc)
    out = soft_expire_source_jobs(
        db,
        source_id=7,
        seen_before=seen,
        dump_complete=False,
        now=seen,
    )
    assert out["closed_stale_aged"] == 3
    assert out["closed_stale_unseen"] == 0
    assert db.execute.call_count == 1
    assert out["stale_after_days"] == STALE_AFTER_DAYS


def test_soft_expire_unseen_when_dump_complete():
    db = MagicMock()
    aged = MagicMock(rowcount=1)
    unseen = MagicMock(rowcount=5)
    db.execute.side_effect = [aged, unseen]
    now = datetime.now(timezone.utc)
    out = soft_expire_source_jobs(
        db,
        source_id=7,
        seen_before=now - timedelta(minutes=5),
        dump_complete=True,
        now=now,
    )
    assert out["closed_stale_aged"] == 1
    assert out["closed_stale_unseen"] == 5
    assert db.execute.call_count == 2
