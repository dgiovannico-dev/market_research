"""Wave 0: CLOSED_JOB_STATUSES shared kernel — no ingestion → analytics import."""

from __future__ import annotations

from pathlib import Path

from app.storage.enums import CLOSED_JOB_STATUSES, JobStatus


def test_closed_job_statuses_canonical():
    assert JobStatus.closed.value in CLOSED_JOB_STATUSES
    assert JobStatus.closed_stale.value in CLOSED_JOB_STATUSES
    assert JobStatus.removed_from_source.value in CLOSED_JOB_STATUSES


def test_ingestion_country_backfill_does_not_import_analytics():
    src = Path(__file__).resolve().parents[1] / "app" / "ingestion" / "country_backfill.py"
    text = src.read_text(encoding="utf-8")
    assert "app.analytics" not in text
    assert "from app.storage.enums import CLOSED_JOB_STATUSES" in text


def test_job_query_reexports_same_tuple():
    from app.analytics.job_query import CLOSED_JOB_STATUSES as from_analytics

    assert from_analytics == CLOSED_JOB_STATUSES
