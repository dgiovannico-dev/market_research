"""Cheap observed DB counts for report materialization (evidence grounding)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.storage.models_core import Job, Source


def get_observed_counts(db: Session, period_days: int = 90) -> dict[str, Any]:
    days = max(1, min(int(period_days), 3660))
    since = datetime.now(UTC) - timedelta(days=days)
    unique_jobs = db.scalar(
        select(func.count())
        .select_from(Job)
        .where(Job.is_canonical.is_(True))
        .where(Job.published_at.is_not(None))
        .where(Job.published_at >= since)
    )
    total_canonical = db.scalar(
        select(func.count()).select_from(Job).where(Job.is_canonical.is_(True))
    )
    sources_total = db.scalar(select(func.count()).select_from(Source))
    sources_enabled = db.scalar(
        select(func.count()).select_from(Source).where(Source.connector_status == "enabled")
    )
    with_rate = db.scalar(
        select(func.count(func.distinct(Job.id)))
        .select_from(Job)
        .join(Job.rates)
        .where(Job.is_canonical.is_(True))
        .where(Job.published_at.is_not(None))
        .where(Job.published_at >= since)
    )
    return {
        "period_days": days,
        "unique_jobs_in_period": int(unique_jobs or 0),
        "canonical_jobs_total": int(total_canonical or 0),
        "jobs_with_rate_in_period": int(with_rate or 0),
        "sources_total": int(sources_total or 0),
        "sources_enabled": int(sources_enabled or 0),
        "evidence_kind": "observed",
        "disclaimer": (
            "Counts are observed records in this database only; not total market size."
        ),
    }
