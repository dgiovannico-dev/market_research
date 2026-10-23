"""Observed DB ops metrics snapshot (not market size)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.scheduler.crawler_summary import count_enabled_intents, load_last_tick_summary
from app.storage.models_core import CollectionRun, Job, Source


def ops_metrics_snapshot(db: Session) -> dict[str, Any]:
    canonical_jobs = db.scalar(select(func.count()).select_from(Job).where(Job.is_canonical.is_(True)))
    sources_total = db.scalar(select(func.count()).select_from(Source))
    sources_enabled = db.scalar(
        select(func.count()).select_from(Source).where(Source.connector_status == "enabled")
    )
    runs_total = db.scalar(select(func.count()).select_from(CollectionRun))
    runs_failed = db.scalar(
        select(func.count())
        .select_from(CollectionRun)
        .where(CollectionRun.status.in_(("failed", "error", "partial")))
    )
    last_run = db.scalars(
        select(CollectionRun).order_by(CollectionRun.started_at.desc()).limit(1)
    ).first()
    last_success = db.scalars(
        select(CollectionRun)
        .where(CollectionRun.status == "succeeded")
        .order_by(CollectionRun.completed_at.desc())
        .limit(1)
    ).first()
    errors_sum = db.scalar(select(func.coalesce(func.sum(CollectionRun.errors_count), 0)))
    dupes_sum = db.scalar(select(func.coalesce(func.sum(CollectionRun.duplicates_detected), 0)))
    intents = count_enabled_intents(db)
    last_tick = load_last_tick_summary(db)

    return {
        "evidence_kind": "observed",
        "disclaimer": "Observed database counters only; not total market size.",
        "jobs_canonical": int(canonical_jobs or 0),
        "sources_total": int(sources_total or 0),
        "sources_enabled": int(sources_enabled or 0),
        "collection_runs_total": int(runs_total or 0),
        "collection_runs_failed": int(runs_failed or 0),
        "collection_errors_sum": int(errors_sum or 0),
        "duplicates_detected_sum": int(dupes_sum or 0),
        "last_run": _run_brief(last_run),
        "last_success_run": _run_brief(last_success),
        "crawler": {
            **intents,
            "last_tick": last_tick,
        },
    }


def _run_brief(run: CollectionRun | None) -> dict[str, Any] | None:
    if run is None:
        return None
    return {
        "id": run.id,
        "source_id": run.source_id,
        "status": run.status,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        "records_inserted": run.records_inserted,
        "errors_count": run.errors_count,
    }
