"""JobSnapshot helpers — skip no-op writes when content unchanged."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.normalization.hashing import content_hash
from app.storage.models import Job, JobSnapshot


def maybe_add_snapshot(
    db: Session,
    *,
    job: Job,
    observed_at: datetime,
    description_hash: Optional[str],
    rate_evidence: Optional[str],
) -> bool:
    """Insert a snapshot when status/content hashes changed. Returns True if written."""
    title_hash = content_hash(job.title_original)
    rate_hash = content_hash(rate_evidence)
    last = db.scalar(
        select(JobSnapshot)
        .where(JobSnapshot.job_id == job.id)
        .order_by(JobSnapshot.observed_at.desc())
        .limit(1)
    )
    if (
        last is not None
        and last.status == job.status
        and last.title_hash == title_hash
        and last.description_hash == description_hash
        and last.rate_hash == rate_hash
    ):
        return False
    db.add(
        JobSnapshot(
            job_id=job.id,
            observed_at=observed_at,
            status=job.status,
            title_hash=title_hash,
            description_hash=description_hash,
            rate_hash=rate_hash,
        )
    )
    return True
