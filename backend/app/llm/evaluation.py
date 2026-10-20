"""Rules re-run consistency check (evaluation stub without gold labels)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.classification.rules import classify_job
from app.storage.models import Job


def evaluate_rules_consistency(db: Session, *, limit: int = 50) -> dict[str, Any]:
    """Compare stored job fields to a fresh rules pass on title+description.

    This is a self-consistency / regression stub, not a gold-label F1 score.
    """
    jobs = db.scalars(
        select(Job)
        .where(Job.is_canonical.is_(True))
        .order_by(Job.id.desc())
        .limit(limit)
    ).all()

    fields = ("contract_type", "remote_type", "country_code", "seniority")
    matches = {f: 0 for f in fields}
    compared = 0
    disagreements: list[dict[str, Any]] = []

    for job in jobs:
        fresh = classify_job(
            title=job.title_original or "",
            description=job.description_original,
            location=job.location_original,
        )
        compared += 1
        for field in fields:
            stored = getattr(job, field, None)
            predicted = getattr(fresh, field, None)
            if stored == predicted:
                matches[field] += 1
            elif len(disagreements) < 15:
                disagreements.append(
                    {
                        "job_id": job.id,
                        "field": field,
                        "stored": stored,
                        "recomputed": predicted,
                    }
                )

    agreement = {
        field: round(matches[field] / compared, 3) if compared else None for field in fields
    }
    overall = (
        round(sum(matches.values()) / (compared * len(fields)), 3) if compared else None
    )
    return {
        "method": "rules_self_consistency",
        "evidence_kind": "derived",
        "jobs_evaluated": compared,
        "field_agreement": agreement,
        "overall_agreement": overall,
        "disagreements_sample": disagreements,
        "limits": (
            "No gold labels. Measures stored vs re-run rules agreement on recent jobs. "
            "LLM path is not scored here unless CLASSIFICATION_MODE uses LLM at ingest."
        ),
    }
