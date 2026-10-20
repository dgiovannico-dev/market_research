from __future__ import annotations

from datetime import datetime, timedelta, timezone
from statistics import mean, median
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.storage.models import Job, JobRate


def _percentile(sorted_vals: list[float], p: float) -> float | None:
    if not sorted_vals:
        return None
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    k = (len(sorted_vals) - 1) * p
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return sorted_vals[f]
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)


def rate_explorer(
    db: Session,
    *,
    days: int = 180,
    country_code: Optional[str] = None,
    unit: Optional[str] = None,
    currency: Optional[str] = None,
    min_sample: int = 5,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=days)
    q = (
        select(JobRate)
        .join(Job)
        .options(joinedload(JobRate.job))
        .where(
            Job.is_canonical.is_(True),
            Job.published_at >= date_from,
            JobRate.amount_min.is_not(None),
            JobRate.rate_type == "advertised",
        )
    )
    if country_code:
        q = q.where(Job.country_code == country_code)
    if unit:
        q = q.where(JobRate.unit == unit)
    if currency:
        q = q.where(JobRate.currency == currency)

    rows = db.scalars(q).unique().all()
    buckets: dict[tuple[str, str, str], list[float]] = {}
    for rate in rows:
        key = (
            rate.job.country_code if rate.job else "unknown",
            rate.currency or "UNK",
            rate.unit or "unknown",
        )
        # Use midpoint when range present; never invent missing amounts
        vals = [v for v in [rate.amount_min, rate.amount_max] if v is not None]
        if not vals:
            continue
        amount = sum(vals) / len(vals)
        buckets.setdefault(key, []).append(amount)

    items = []
    for (country, curr, u), amounts in buckets.items():
        amounts_sorted = sorted(amounts)
        n = len(amounts_sorted)
        stable = n >= min_sample
        items.append(
            {
                "country_code": country,
                "currency": curr,
                "unit": u,
                "sample_size": n,
                "min": amounts_sorted[0],
                "max": amounts_sorted[-1],
                "mean": mean(amounts_sorted),
                "median": median(amounts_sorted),
                "p10": _percentile(amounts_sorted, 0.10) if stable else None,
                "p25": _percentile(amounts_sorted, 0.25) if stable else None,
                "p75": _percentile(amounts_sorted, 0.75) if stable else None,
                "p90": _percentile(amounts_sorted, 0.90) if stable else None,
                "status": "ok" if stable else "insufficient_data",
                "evidence_kind": "derived",
                "rate_type": "advertised",
                "limits": (
                    "Advertised rates only. Hourly and daily are not mixed. "
                    "Small samples are flagged. Not causal skill→rate proof."
                ),
            }
        )
    items.sort(key=lambda x: (-x["sample_size"], x["country_code"]))
    return {
        "period_days": days,
        "min_sample": min_sample,
        "jobs_with_rates": len(rows),
        "disclaimer": "Observed published rates in DB only; missing rates stay NULL and are excluded.",
        "items": items,
    }
