from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.storage.models import Job, JobSkill


def skill_cooccurrence(
    db: Session,
    *,
    days: int = 90,
    min_support: int = 3,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=days)
    jobs = db.scalars(
        select(Job)
        .options(joinedload(Job.skills).joinedload(JobSkill.technology))
        .where(Job.is_canonical.is_(True), Job.published_at >= date_from)
    ).unique().all()

    single = Counter()
    pair = Counter()
    for job in jobs:
        names = sorted({s.technology.canonical_name for s in job.skills if s.technology})
        for n in names:
            single[n] += 1
        for i, a in enumerate(names):
            for b in names[i + 1 :]:
                pair[(a, b)] += 1

    n_jobs = len(jobs) or 1
    items = []
    for (a, b), count in pair.items():
        if count < min_support:
            continue
        # Lift vs independence assumption
        p_a = single[a] / n_jobs
        p_b = single[b] / n_jobs
        p_ab = count / n_jobs
        expected = p_a * p_b
        lift = (p_ab / expected) if expected > 0 else None
        jaccard = count / (single[a] + single[b] - count) if (single[a] + single[b] - count) else None
        items.append(
            {
                "tech_a": a,
                "tech_b": b,
                "support": count,
                "lift": round(lift, 3) if lift is not None else None,
                "jaccard": round(jaccard, 3) if jaccard is not None else None,
                "freq_a": single[a],
                "freq_b": single[b],
                "evidence_kind": "derived",
                "limits": "Co-occurrence is not causation. Sample limited to stored jobs.",
            }
        )
    items.sort(key=lambda x: (-x["support"], -(x["lift"] or 0)))
    return {
        "period_days": days,
        "min_support": min_support,
        "jobs_analyzed": len(jobs),
        "items": items[:200],
    }
