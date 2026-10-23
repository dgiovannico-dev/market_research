"""Rematch existing corpus jobs to research intents (no crawl)."""

from __future__ import annotations

from typing import Any, Literal, Optional

from sqlalchemy.orm import Session

from app.research.match_backfill import backfill_intent_matches

IntentKind = Literal["focus", "discovery", "all"]


def rematch_intents(
    db: Session,
    *,
    kind: IntentKind = "all",
    enabled_only: bool = True,
    dry_run: bool = False,
    limit_jobs: Optional[int] = None,
) -> dict[str, Any]:
    result = backfill_intent_matches(
        db,
        kind=kind,
        enabled_only=enabled_only,
        limit_jobs=limit_jobs,
        dry_run=dry_run,
    )
    if not dry_run:
        db.commit()
    return result
