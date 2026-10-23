"""Budgeted manual sync for one research intent (ADR-007 fan-out)."""

from __future__ import annotations

from typing import Any, Optional

import structlog
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.collection.run_source import run_source
from app.application.ports.driven.collector_gateway import CollectorGateway
from app.application.ports.driven.job_write import JobWritePort
from app.bootstrap import get_container
from app.collectors.base import simplify_query_for
from app.storage.models import SearchQuery, Source

log = structlog.get_logger()


def _pick_sources_for_intent(
    db: Session,
    collectors: CollectorGateway,
    *,
    limit: int,
) -> list[Source]:
    """Prefer search-mode enabled sources; fall back to all enabled collectors."""
    sources = list(
        db.scalars(
            select(Source).where(
                Source.enabled.is_(True),
                Source.connector_status == "enabled",
            )
        ).all()
    )
    search_keys = set(collectors.keys_by_mode("search"))
    if search_keys:
        preferred = [s for s in sources if (s.connector_type or "") in search_keys]
        if preferred:
            sources = preferred
    out: list[Source] = []
    for source in sources:
        if not collectors.get(source.connector_type or ""):
            continue
        out.append(source)
        if len(out) >= limit:
            break
    return out


async def sync_research_intent(
    db: Session,
    intent: SearchQuery,
    *,
    max_collectors: Optional[int] = None,
    collectors: CollectorGateway | None = None,
    job_write: JobWritePort | None = None,
) -> dict[str, Any]:
    """Run a budgeted collector subset for one intent; upserts job_intent_matches."""
    query_text = (intent.query_text or "").strip()
    if not query_text:
        return {
            "query_id": intent.id,
            "status": "skipped",
            "reason": "missing_query",
            "collections": [],
        }

    container = get_container()
    gateway = collectors or container.collectors
    writes = job_write or container.job_write
    limit = (
        max_collectors
        if max_collectors is not None
        else container.settings.sync_max_collector_calls_per_intent
    )
    sources = _pick_sources_for_intent(db, gateway, limit=max(1, limit))
    results: list[dict[str, Any]] = []

    for source in sources:
        collector = gateway.get(source.connector_type or "")
        if not collector:
            continue
        q = simplify_query_for(collector, query_text)
        outcome = await run_source(
            db,
            source=source,
            collector=collector,
            query=q,
            query_id=intent.id,
            collection_method="intent_sync",
            job_write=writes,
        )
        if outcome.get("error"):
            log.error(
                "intent_sync_failed",
                source=source.name,
                query_id=intent.id,
                error=outcome["error"],
            )
            results.append({"source": source.name, "error": outcome["error"]})
        else:
            results.append(
                {
                    "source": source.name,
                    "run_id": outcome.get("run_id"),
                    "status": outcome.get("status"),
                    "inserted": outcome.get("inserted"),
                    "updated": outcome.get("updated"),
                    "duplicates": outcome.get("duplicates"),
                    "errors": outcome.get("errors"),
                    "collector_errors": outcome.get("collector_errors") or [],
                    "skipped": outcome.get("skipped"),
                    "reason": outcome.get("reason"),
                }
            )

    return {
        "query_id": intent.id,
        "status": "ok",
        "query_text": query_text,
        "collections": results,
    }
