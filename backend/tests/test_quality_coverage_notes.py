"""DSS quality by_source pct_thin, coverage footnotes, countries closed filter."""

from __future__ import annotations

import inspect
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from sqlalchemy import func, select
from sqlalchemy.dialects import postgresql

import app.analytics.countries as countries_mod
from app.analytics.coverage_notes import attach_coverage_notes, coverage_notes_for_slice
from app.analytics.job_query import CLOSED_JOB_STATUSES, base_job_query
from app.analytics.quality import data_quality_report
from app.storage.enums import JobStatus
from app.storage.models import Job, Source


def _compile(stmt, *, literal_binds: bool = False) -> str:
    return str(
        stmt.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": literal_binds},
        )
    )


def test_closed_job_statuses_includes_closed_stale():
    assert JobStatus.closed_stale.value in CLOSED_JOB_STATUSES


def test_country_open_jobs_mirror_excludes_closed_stale():
    """Same status filter as country_comparison open_jobs base."""
    date_from = datetime.now(timezone.utc) - timedelta(days=90)
    open_jobs = (
        Job.is_canonical.is_(True),
        Job.published_at >= date_from,
        Job.status.notin_(CLOSED_JOB_STATUSES),
    )
    stmt = select(func.count()).select_from(select(Job).where(*open_jobs).subquery())
    sql = _compile(stmt).lower()
    assert "not in" in sql or "notin" in sql
    assert JobStatus.closed_stale.value in CLOSED_JOB_STATUSES


def test_countries_module_uses_closed_job_statuses_constant():
    src = inspect.getsource(countries_mod)
    assert "CLOSED_JOB_STATUSES" in src
    assert "Job.status.notin_(CLOSED_JOB_STATUSES)" in src


@patch("app.analytics.quality.resolve_job_id_subquery", return_value=None)
def test_data_quality_by_source_includes_pct_thin(mock_subq):
    db = MagicMock(name="db")
    last_seen = datetime(2026, 10, 1, tzinfo=timezone.utc)
    src = SimpleNamespace(
        id=1,
        name="TestSource",
        connector_type="remoteok",
        connector_status="active",
        enabled=True,
        last_success_at=None,
        last_error=None,
        coverage_notes=None,
    )

    db.scalar.side_effect = [10, 8, 9, 7, 2, 5, 1]
    by_source_rows = MagicMock()
    by_source_rows.all.return_value = [(1, 10, 8, 3, last_seen)]
    rate_rows = MagicMock()
    rate_rows.all.return_value = [(1, 4)]
    db.execute.side_effect = [by_source_rows, rate_rows]

    scalars_calls = {"n": 0}

    def _scalars(_stmt):
        scalars_calls["n"] += 1
        out = MagicMock()
        out.all.return_value = [src] if scalars_calls["n"] == 1 else []
        return out

    db.scalars.side_effect = _scalars

    out = data_quality_report(db, lens="market")

    assert out["metrics"]["pct_thin"] == 20.0
    assert out["metrics"]["thin_n"] == 2
    assert len(out["by_source"]) == 1
    row = out["by_source"][0]
    assert row["pct_thin"] == 30.0
    assert row["n"] == 10
    assert row["name"] == "TestSource"
    mock_subq.assert_called_once()


def test_coverage_notes_mentions_thin_evidence():
    db = MagicMock(name="db")
    db.scalar.side_effect = [100, 25]
    source_ids = MagicMock()
    source_ids.all.return_value = [(1,)]
    db.execute.return_value = source_ids
    db.scalars.return_value.all.return_value = [
        SimpleNamespace(connector_type="remoteok"),
    ]

    notes = coverage_notes_for_slice(db, country_code="IT")

    assert len(notes) == 1
    note = notes[0]
    assert note["code"] == "thin_evidence"
    assert note["thin_n"] == 25
    assert note["pct"] == 25.0
    assert "thin evidence" in note["message"].lower()
    assert "25 jobs (25.0%)" in note["message"]
    assert "min_evidence=standard" in note["message"]


def test_coverage_notes_empty_when_no_thin_jobs():
    db = MagicMock(name="db")
    db.scalar.side_effect = [50, 0]

    assert coverage_notes_for_slice(db) == []


def test_attach_coverage_notes_adds_key_when_present():
    payload = {"countries": ["IT"]}
    attach_coverage_notes(payload, ["footnote"])
    assert payload["coverage_notes"] == ["footnote"]

    bare = {"x": 1}
    attach_coverage_notes(bare, [])
    assert "coverage_notes" not in bare


def test_base_job_query_aligns_with_countries_closed_filter():
    """Quality/coverage corpus uses the same closed-status exclusion."""
    sql = _compile(base_job_query()).lower()
    assert "is_canonical" in sql
    assert ("not in" in sql or "notin" in sql) and CLOSED_JOB_STATUSES == (
        JobStatus.closed.value,
        JobStatus.closed_stale.value,
        JobStatus.removed_from_source.value,
    )
