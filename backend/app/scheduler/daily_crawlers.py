"""Budgeted daily crawlers: dump/feed → discovery → focus (SPEC-research-intents §6)."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Protocol

import structlog
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.bootstrap import get_container
from app.collectors.base import BaseCollector, simplify_query_for
from app.collectors.registry import COLLECTOR_GEO, get_collector
from app.core.config import get_settings
from app.scheduler.crawl_run import crawl_one
from app.scheduler.crawler_summary import (
    build_tick_summary,
    count_enabled_intents,
    load_last_tick_summary,
    persist_crawler_tick,
)
from app.scheduler.tick_state import already_succeeded, mark_succeeded
from app.storage.models import SearchQuery, Source

log = structlog.get_logger()

SourceCollector = tuple[Source, BaseCollector]


class IntentLike(Protocol):
    id: int
    query_text: str
    countries: list[str] | None


def utc_today() -> date:
    return datetime.now(timezone.utc).date()


def _collection_mode(collector: BaseCollector) -> str:
    return getattr(collector, "collection_mode", "search") or "search"


def pick_search_collectors(
    intent: IntentLike,
    search_pool: list[SourceCollector],
    lim: int,
    global_left: int,
    day_ordinal: int,
) -> list[SourceCollector]:
    """Stable rotation by (UTC day + intent.id); prefer geo-matching sources."""
    n = min(lim, global_left, len(search_pool))
    if n <= 0:
        return []

    ordered = sorted(search_pool, key=lambda sc: sc[1].source_key)
    offset = (day_ordinal + int(intent.id)) % len(ordered)
    ordered = ordered[offset:] + ordered[:offset]

    countries = {str(c).upper() for c in (intent.countries or []) if c}
    if countries:
        preferred: list[SourceCollector] = []
        others: list[SourceCollector] = []
        for item in ordered:
            geo = COLLECTOR_GEO.get(item[1].source_key, frozenset())
            if geo & countries:
                preferred.append(item)
            else:
                others.append(item)
        ordered = preferred + others

    return ordered[:n]


def _load_enabled_sources(db: Session) -> list[Source]:
    return list(
        db.scalars(
            select(Source).where(Source.enabled.is_(True), Source.connector_status == "enabled")
        ).all()
    )


def _partition_sources(
    sources: list[Source],
) -> tuple[list[SourceCollector], list[SourceCollector]]:
    dump_feed: list[SourceCollector] = []
    search: list[SourceCollector] = []
    for source in sources:
        key = source.connector_type or ""
        collector = get_collector(key)
        if not collector:
            continue
        if not get_container().credentials.has_credentials(key):
            continue
        pair = (source, collector)
        if _collection_mode(collector) in ("dump", "feed"):
            dump_feed.append(pair)
        else:
            search.append(pair)
    dump_feed.sort(key=lambda sc: sc[1].source_key)
    search.sort(key=lambda sc: sc[1].source_key)
    return dump_feed, search


def _scheduled_intents(db: Session, kind: str, limit: int) -> list[SearchQuery]:
    rows = db.scalars(
        select(SearchQuery)
        .where(
            SearchQuery.enabled.is_(True),
            SearchQuery.kind == kind,
            SearchQuery.deleted_at.is_(None),
            SearchQuery.schedule_hint != "manual_only",
        )
        .order_by(SearchQuery.id)
        .limit(limit)
    ).all()
    return list(rows)


async def _run_intent_phase(
    db: Session,
    *,
    intents: list[SearchQuery],
    search_pool: list[SourceCollector],
    phase: str,
    per_intent: int,
    max_total: int,
    calls: int,
    day_ordinal: int,
    collections: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
    errors: list[dict[str, Any]],
) -> tuple[int, int]:
    ran = 0
    for intent in intents:
        if calls >= max_total:
            skipped.append(
                {
                    "query_id": intent.id,
                    "phase": phase,
                    "skipped": True,
                    "reason": "budget",
                }
            )
            continue
        subset = pick_search_collectors(
            intent,
            search_pool,
            lim=per_intent,
            global_left=max_total - calls,
            day_ordinal=day_ordinal,
        )
        if not subset:
            if search_pool:
                skipped.append(
                    {
                        "query_id": intent.id,
                        "phase": phase,
                        "skipped": True,
                        "reason": "budget",
                    }
                )
            continue
        for source, collector in subset:
            q = simplify_query_for(collector, intent.query_text)
            result = await crawl_one(
                db,
                source=source,
                collector=collector,
                query=q or None,
                query_id=intent.id,
                phase=phase,
            )
            collections.append(result)
            if result.get("skipped"):
                skipped.append(result)
                if result.get("run_id") is not None:
                    calls += 1
                    ran += 1
                continue
            if result.get("error"):
                errors.append(result)
            calls += 1
            ran += 1
            if calls >= max_total:
                break
    return calls, ran


async def run_daily_crawlers(*, force: bool = False) -> dict[str, Any]:
    """Dump/feed once, then budgeted discovery then focus search collectors."""
    settings = get_settings()
    day = utc_today()
    day_ordinal = day.timetuple().tm_yday
    max_total = settings.sync_max_total_collector_calls_per_tick
    per_intent = settings.sync_max_collector_calls_per_intent

    if not force and already_succeeded(day):
        summary: dict[str, Any] | None = None
        try:
            with get_container().session_scope() as db_peek:
                summary = load_last_tick_summary(db_peek)
                intents_enabled = count_enabled_intents(db_peek)
        except Exception:  # noqa: BLE001
            intents_enabled = {
                "discovery_intents_enabled": 0,
                "focus_intents_enabled": 0,
            }
        if summary is None:
            summary = build_tick_summary(
                day=day,
                status="skipped_idempotent",
                idempotent=True,
                dump_ran=0,
                discovery_ran=0,
                focus_ran=0,
                calls=0,
                discovery_scheduled=0,
                focus_scheduled=0,
                intents_enabled=intents_enabled,
                skipped=[],
                errors=[],
            )
        else:
            summary = {
                **summary,
                "status": "skipped_idempotent",
                "idempotent": True,
                **intents_enabled,
            }
        return {
            "status": "skipped_idempotent",
            "idempotent": True,
            "day": day.isoformat(),
            "dump_ran": 0,
            "discovery_ran": 0,
            "focus_ran": 0,
            "calls": 0,
            "summary": summary,
            "skipped": [],
            "errors": [],
            "collections": [],
        }

    db = get_container().open_session()
    try:
        sources = _load_enabled_sources(db)
        dump_feed, search_pool = _partition_sources(sources)
        discovery = _scheduled_intents(db, "discovery", settings.sync_max_discovery_per_tick)
        focus = _scheduled_intents(db, "focus", settings.sync_max_focus_per_tick)
        intents_enabled = count_enabled_intents(db)

        collections: list[dict[str, Any]] = []
        skipped: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []
        calls = 0
        dump_ran = 0

        for source, collector in dump_feed:
            if calls >= max_total:
                break
            result = await crawl_one(
                db,
                source=source,
                collector=collector,
                query=None,
                query_id=None,
                phase="dump",
            )
            collections.append(result)
            if result.get("error"):
                errors.append(result)
            calls += 1
            dump_ran += 1

        calls, discovery_ran = await _run_intent_phase(
            db,
            intents=discovery,
            search_pool=search_pool,
            phase="discovery",
            per_intent=per_intent,
            max_total=max_total,
            calls=calls,
            day_ordinal=day_ordinal,
            collections=collections,
            skipped=skipped,
            errors=errors,
        )
        calls, focus_ran = await _run_intent_phase(
            db,
            intents=focus,
            search_pool=search_pool,
            phase="focus",
            per_intent=per_intent,
            max_total=max_total,
            calls=calls,
            day_ordinal=day_ordinal,
            collections=collections,
            skipped=skipped,
            errors=errors,
        )

        status = "partial" if errors else "succeeded"
        completed_at = datetime.now(timezone.utc)
        summary = build_tick_summary(
            day=day,
            status=status,
            idempotent=False,
            dump_ran=dump_ran,
            discovery_ran=discovery_ran,
            focus_ran=focus_ran,
            calls=calls,
            discovery_scheduled=len(discovery),
            focus_scheduled=len(focus),
            intents_enabled=intents_enabled,
            skipped=skipped,
            errors=errors,
            completed_at=completed_at,
        )
        persist_crawler_tick(db, day=day, status=status, summary=summary)
        mark_succeeded(day)
        return {
            "status": status,
            "idempotent": False,
            "day": day.isoformat(),
            "ran_at": completed_at.isoformat(),
            "dump_ran": dump_ran,
            "discovery_ran": discovery_ran,
            "focus_ran": focus_ran,
            "calls": calls,
            "summary": summary,
            "skipped": skipped,
            "errors": errors,
            "collections": collections,
        }
    except Exception as exc:  # noqa: BLE001
        log.error("daily_crawlers_failed", error=str(exc))
        raise
    finally:
        db.close()
