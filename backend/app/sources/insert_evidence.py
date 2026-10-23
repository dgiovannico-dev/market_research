"""Per-source CollectionRun insert evidence for ops / Sources UI."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.storage.models import CollectionRun


def insert_evidence_by_source_id(db: Session) -> dict[int, dict[str, Any]]:
    """Map source_id → insert_runs_count + last_insert_at (runs with records_inserted > 0)."""
    rows = db.execute(
        select(
            CollectionRun.source_id,
            func.count().label("insert_runs_count"),
            func.max(CollectionRun.completed_at).label("last_insert_at"),
        )
        .where(CollectionRun.records_inserted > 0)
        .group_by(CollectionRun.source_id)
    ).all()
    out: dict[int, dict[str, Any]] = {}
    for row in rows:
        last: datetime | None = row.last_insert_at
        out[int(row.source_id)] = {
            "insert_runs_count": int(row.insert_runs_count or 0),
            "last_insert_at": last.isoformat() if last else None,
            "has_insert_evidence": True,
        }
    return out


def empty_insert_evidence() -> dict[str, Any]:
    return {
        "insert_runs_count": 0,
        "last_insert_at": None,
        "has_insert_evidence": False,
    }
