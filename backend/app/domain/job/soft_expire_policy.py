"""Pure soft-expire decision — no SQLAlchemy (ADR-008 Wave 3b)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.storage.enums import JobStatus

STALE_AFTER_DAYS = 45

ACTIVE_STATUSES: tuple[str, ...] = (
    JobStatus.active_verified.value,
    JobStatus.active_unverified.value,
    JobStatus.stale.value,
    JobStatus.unknown.value,
)

CLOSED_STALE = JobStatus.closed_stale.value


@dataclass(frozen=True)
class SoftExpirePlan:
    """Inputs for the persistence adapter's UPDATE statements."""

    clock: datetime
    age_cutoff: datetime
    seen_before: datetime
    run_unseen_expire: bool
    stale_after_days: int
    closed_status: str
    active_statuses: tuple[str, ...]


def _aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def plan_soft_expire(
    *,
    seen_before: datetime,
    dump_complete: bool = False,
    stale_after_days: int = STALE_AFTER_DAYS,
    now: datetime | None = None,
) -> SoftExpirePlan:
    """Decide cutoffs and whether unseen-from-dump expire is allowed.

    Capped/partial dumps must pass ``dump_complete=False`` so the adapter does
    not mass-close jobs missing from a sample.
    """
    clock = _aware(now or datetime.now(timezone.utc))
    seen = _aware(seen_before)
    return SoftExpirePlan(
        clock=clock,
        age_cutoff=clock - timedelta(days=stale_after_days),
        seen_before=seen,
        run_unseen_expire=bool(dump_complete),
        stale_after_days=stale_after_days,
        closed_status=CLOSED_STALE,
        active_statuses=ACTIVE_STATUSES,
    )
