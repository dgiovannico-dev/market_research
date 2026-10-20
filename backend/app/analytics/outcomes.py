from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.storage.models import ApplicationOutcome


def outcomes_summary(db: Session, profile_id: int) -> dict[str, Any]:
    rows = db.scalars(
        select(ApplicationOutcome).where(ApplicationOutcome.profile_id == profile_id)
    ).all()
    n = len(rows)
    if n == 0:
        return {
            "profile_id": profile_id,
            "applications": 0,
            "metrics": {},
            "disclaimer": "Personal metrics only; not market metrics.",
        }

    responses = sum(1 for r in rows if r.response)
    interviews = sum(1 for r in rows if r.interview)
    offers = sum(1 for r in rows if (r.outcome or "").lower() in {"offer", "won", "hired", "accepted"})
    by_channel: dict[str, int] = {}
    for r in rows:
        ch = r.channel or "unknown"
        by_channel[ch] = by_channel.get(ch, 0) + 1

    return {
        "profile_id": profile_id,
        "applications": n,
        "metrics": {
            "response_rate": round(responses / n, 4),
            "interview_rate": round(interviews / n, 4),
            "offer_rate": round(offers / n, 4),
            "by_channel": by_channel,
        },
        "evidence_kind": "manually_verified",
        "disclaimer": "Personal pipeline metrics only. Do not generalize to market without adequate sample.",
    }
