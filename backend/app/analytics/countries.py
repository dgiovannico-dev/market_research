from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.storage.models import Job, JobRate, JobSkill, Technology

FOCUS_COUNTRIES = ["IT", "CH", "DE", "AT", "FR", "NL", "BE", "LU", "IE", "ES", "GB", "US", "WW", "unknown"]


def country_comparison(db: Session, *, days: int = 90) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=days)
    base = select(Job).where(Job.is_canonical.is_(True), Job.published_at >= date_from)

    items = []
    for code in FOCUS_COUNTRIES:
        q = base.where(Job.country_code == code)
        total = db.scalar(select(func.count()).select_from(q.subquery())) or 0
        if total == 0:
            continue
        remote = db.scalar(
            select(func.count()).select_from(q.where(Job.remote_type == "remote").subquery())
        ) or 0
        b2b = db.scalar(
            select(func.count()).select_from(
                q.where(Job.contract_type.in_(["freelance", "b2b", "contractor"])).subquery()
            )
        ) or 0
        allowed = db.scalar(
            select(func.count()).select_from(
                q.where(Job.residence_restriction == "explicitly_allowed").subquery()
            )
        ) or 0
        restricted = db.scalar(
            select(func.count()).select_from(
                q.where(Job.residence_restriction == "explicitly_restricted").subquery()
            )
        ) or 0
        with_rate = db.scalar(
            select(func.count(func.distinct(JobRate.job_id)))
            .select_from(JobRate)
            .join(Job)
            .where(
                Job.is_canonical.is_(True),
                Job.published_at >= date_from,
                Job.country_code == code,
            )
        ) or 0
        top_tech = db.execute(
            select(Technology.canonical_name, func.count(JobSkill.id))
            .join(JobSkill)
            .join(Job)
            .where(
                Job.is_canonical.is_(True),
                Job.published_at >= date_from,
                Job.country_code == code,
            )
            .group_by(Technology.canonical_name)
            .order_by(func.count(JobSkill.id).desc())
            .limit(5)
        ).all()
        items.append(
            {
                "country_code": code,
                "jobs_observed": total,
                "remote_share": round(remote / total, 4),
                "b2b_freelance_share": round(b2b / total, 4),
                "explicitly_allowed_residence": allowed,
                "explicitly_restricted_residence": restricted,
                "unclear_residence": total - allowed - restricted,
                "jobs_with_rate": with_rate,
                "top_technologies": [{"name": n, "mentions": c} for n, c in top_tech],
                "evidence_kind": "derived",
                "legal_disclaimer": (
                    "Not legal/tax advice. Residence access categories are text-extracted; "
                    "remote != acceptance of Italian residents."
                ),
            }
        )

    return {
        "period_days": days,
        "disclaimer": "Observed jobs by country_code in this DB; not full market census.",
        "items": items,
    }
