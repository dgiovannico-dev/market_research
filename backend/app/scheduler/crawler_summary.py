"""Thin daily-crawler tick summaries for ops (no full collection payloads)."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.storage.models import CrawlerTick, SearchQuery


def count_enabled_intents(db: Session) -> dict[str, int]:
    """Enabled discovery/focus intents (not deleted), regardless of schedule_hint."""

    def _count(kind: str) -> int:
        return int(
            db.scalar(
                select(func.count())
                .select_from(SearchQuery)
                .where(
                    SearchQuery.enabled.is_(True),
                    SearchQuery.kind == kind,
                    SearchQuery.deleted_at.is_(None),
                )
            )
            or 0
        )

    return {
        "discovery_intents_enabled": _count("discovery"),
        "focus_intents_enabled": _count("focus"),
    }


def summarize_skip_reasons(skipped: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in skipped:
        reason = str(item.get("reason") or "unknown")
        counts[reason] = counts.get(reason, 0) + 1
    return counts


def build_tick_summary(
    *,
    day: date,
    status: str,
    idempotent: bool,
    dump_ran: int,
    discovery_ran: int,
    focus_ran: int,
    calls: int,
    discovery_scheduled: int,
    focus_scheduled: int,
    intents_enabled: dict[str, int],
    skipped: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    completed_at: datetime | None = None,
) -> dict[str, Any]:
    """Compact tick snapshot suitable for crawler_ticks.summary and ops/metrics."""
    done = completed_at or datetime.now(timezone.utc)
    return {
        "day": day.isoformat(),
        "status": status,
        "idempotent": idempotent,
        "discovery_intents_enabled": intents_enabled.get("discovery_intents_enabled", 0),
        "focus_intents_enabled": intents_enabled.get("focus_intents_enabled", 0),
        "discovery_intents_scheduled": discovery_scheduled,
        "focus_intents_scheduled": focus_scheduled,
        "dump_ran": dump_ran,
        "discovery_ran": discovery_ran,
        "focus_ran": focus_ran,
        "calls": calls,
        "errors_count": len(errors),
        "skips": summarize_skip_reasons(skipped),
        "completed_at": done.isoformat(),
    }


def persist_crawler_tick(
    db: Session,
    *,
    day: date,
    status: str,
    summary: dict[str, Any],
) -> None:
    row = db.get(CrawlerTick, day)
    if row is None:
        row = CrawlerTick(day=day, status=status, summary=summary)
        db.add(row)
    else:
        row.status = status
        row.summary = summary
    row.completed_at = datetime.now(timezone.utc)
    db.commit()


def load_last_tick_summary(db: Session) -> dict[str, Any] | None:
    row = db.scalars(select(CrawlerTick).order_by(CrawlerTick.day.desc()).limit(1)).first()
    if row is None:
        return None
    summary = dict(row.summary or {})
    summary.setdefault("day", row.day.isoformat())
    summary.setdefault("status", row.status)
    summary.setdefault("skips", {})
    if "idempotent" not in summary:
        summary["idempotent"] = summary.get("status") == "skipped_idempotent"
    if row.completed_at and "completed_at" not in summary:
        summary["completed_at"] = row.completed_at.isoformat()
    return summary
