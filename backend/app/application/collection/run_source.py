"""Single CollectionRun: collect → ingest → optional soft-expire.

Shared by the HTTP driver (`POST /sources/{id}/run`) and the daily crawler
(ADR-008 Wave 1). Callers map the returned dict to their response shape.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import structlog
from sqlalchemy.orm import Session

from app.application.collection.ingest_batch import ingest_batch, soft_expire_batch
from app.application.ports.driven.job_write import JobWritePort
from app.collectors.base import (
    MISSING_QUERY,
    BaseCollector,
    CollectorResult,
    is_blank_query,
)
from app.collectors.registry import get_collection_mode
from app.storage.models import CollectionRun, Source

log = structlog.get_logger()


def _is_missing_query_only(errors: list[str]) -> bool:
    cleaned = [e for e in errors if e]
    return bool(cleaned) and all(e == MISSING_QUERY for e in cleaned)


async def run_source(
    db: Session,
    *,
    source: Source,
    collector: BaseCollector,
    query: str | None = None,
    query_id: int | None = None,
    phase: str | None = None,
    collection_method: str = "api",
    job_write: JobWritePort | None = None,
) -> dict[str, Any]:
    """Run one source collection end-to-end.

    When ``query_id`` is set and ``query`` is blank, skips without opening a run
    (intent sync must not invent a topic). Soft-expire runs for dump/feed modes.
    """
    base = {
        "source": source.name,
        "connector": collector.source_key,
        "query_id": query_id,
        "phase": phase,
    }

    if query_id is not None and is_blank_query(query):
        return {**base, "skipped": True, "reason": MISSING_QUERY}

    started = datetime.now(timezone.utc)
    run = CollectionRun(
        source_id=source.id,
        query_id=query_id,
        started_at=started,
        status="running",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        collected: CollectorResult = await collector.collect(query=query)
        if _is_missing_query_only(collected.errors):
            completed = datetime.now(timezone.utc)
            run.completed_at = completed
            run.status = "skipped"
            run.pages_scanned = collected.pages_scanned
            run.records_received = 0
            run.error_summary = MISSING_QUERY
            run.duration_seconds = (completed - started).total_seconds()
            db.commit()
            return {
                **base,
                "run_id": run.id,
                "status": run.status,
                "skipped": True,
                "reason": MISSING_QUERY,
            }

        stats = ingest_batch(
            db,
            source_id=source.id,
            raw_jobs=collected.records,
            query_id=query_id,
            collection_method=collection_method,
            port=job_write,
        )
        expire_stats: dict[str, Any] = {}
        mode = get_collection_mode(collector)
        if mode in ("dump", "feed"):
            expire_stats = soft_expire_batch(
                db,
                source_id=source.id,
                seen_before=started,
                dump_complete=bool(collected.dump_complete),
                port=job_write,
            )
            db.commit()

        completed = datetime.now(timezone.utc)
        run.completed_at = completed
        run.status = "partial" if collected.errors else "succeeded"
        run.pages_scanned = collected.pages_scanned
        run.records_received = len(collected.records)
        run.records_inserted = stats["inserted"]
        run.records_updated = stats["updated"]
        run.duplicates_detected = stats["duplicates"]
        run.errors_count = stats["errors"] + len(collected.errors)
        run.error_summary = (
            "; ".join(collected.errors)[:2000] if collected.errors else None
        )
        run.duration_seconds = (completed - started).total_seconds()
        if collected.meta:
            run.summary = {
                **collected.meta,
                "records": len(collected.records),
                "inserted": stats["inserted"],
                "updated": stats["updated"],
                "duplicates": stats["duplicates"],
                "errors": stats["errors"],
                **expire_stats,
            }
        source.last_success_at = completed
        if run.error_summary:
            source.last_error = run.error_summary
            source.last_error_at = completed
        else:
            source.last_error = None
        db.commit()
        return {
            **base,
            "run_id": run.id,
            "status": run.status,
            "records_received": run.records_received,
            "collector_errors": list(collected.errors),
            **stats,
            **expire_stats,
        }
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        source.last_error = str(exc)
        source.last_error_at = datetime.now(timezone.utc)
        db.commit()
        log.error("collector_failed", source=source.name, error=str(exc))
        return {**base, "error": str(exc)}
