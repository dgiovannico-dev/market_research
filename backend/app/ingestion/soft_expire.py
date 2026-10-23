"""Soft-expire jobs not refreshed by dump crawls (or aged past stale window)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.domain.job.soft_expire_policy import STALE_AFTER_DAYS, plan_soft_expire
from app.storage.models import Job

# Re-export for callers/tests that imported the constant from this module.
__all__ = ["STALE_AFTER_DAYS", "soft_expire_source_jobs"]


def soft_expire_source_jobs(
    db: Session,
    *,
    source_id: int,
    seen_before: datetime,
    dump_complete: bool = False,
    stale_after_days: int = STALE_AFTER_DAYS,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Mark source jobs as ``closed_stale`` when aged or missing from a full dump.

    Policy (cutoffs / dump_complete gate) lives in ``domain.job.soft_expire_policy``.
    """
    plan = plan_soft_expire(
        seen_before=seen_before,
        dump_complete=dump_complete,
        stale_after_days=stale_after_days,
        now=now,
    )

    age_result = db.execute(
        update(Job)
        .where(
            Job.source_id == source_id,
            Job.is_canonical.is_(True),
            Job.status.in_(plan.active_statuses),
            Job.last_seen_at < plan.age_cutoff,
        )
        .values(status=plan.closed_status, closed_at=plan.clock)
    )
    aged = int(age_result.rowcount or 0)

    unseen = 0
    if plan.run_unseen_expire:
        unseen_result = db.execute(
            update(Job)
            .where(
                Job.source_id == source_id,
                Job.is_canonical.is_(True),
                Job.status.in_(plan.active_statuses),
                Job.last_seen_at < plan.seen_before,
            )
            .values(status=plan.closed_status, closed_at=plan.clock)
        )
        unseen = int(unseen_result.rowcount or 0)

    db.flush()
    return {
        "closed_stale_aged": aged,
        "closed_stale_unseen": unseen,
        "dump_complete": dump_complete,
        "stale_after_days": plan.stale_after_days,
    }
