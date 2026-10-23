from __future__ import annotations

from datetime import datetime, timedelta, timezone
from statistics import mean, median
from typing import Any, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.analytics.country_filter import parse_country_codes
from app.analytics.evidence_gate import (
    DEFAULT_MIN_EVIDENCE,
    count_thin_in_query,
    evidence_meta,
    parse_min_evidence,
)
from app.analytics.job_query import base_job_query
from app.analytics.lenses import compare_counts, parse_lens, resolve_job_id_subquery
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
    lens: str = "market",
    query_ids: Optional[Sequence[int]] = None,
    min_evidence: Optional[str] = DEFAULT_MIN_EVIDENCE,
) -> dict[str, Any]:
    lens_name = parse_lens(lens)
    job_id_subq = resolve_job_id_subquery(db, lens_name, query_ids)
    codes = parse_country_codes(country_code)
    tier = parse_min_evidence(min_evidence)
    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=days)
    corpus = base_job_query(
        date_from=date_from,
        country_codes=codes,
        job_id_subq=job_id_subq,
        min_evidence=None,
    )
    excluded_thin_n = count_thin_in_query(db, corpus) if tier == "standard" else 0
    job_corpus = base_job_query(
        date_from=date_from,
        country_codes=codes,
        job_id_subq=job_id_subq,
        min_evidence=tier,
    )
    job_ids = select(job_corpus.with_only_columns(Job.id).subquery().c.id)
    cond = [
        JobRate.job_id.in_(job_ids),
        JobRate.amount_min.is_not(None),
        JobRate.rate_type == "advertised",
    ]
    q = (
        select(JobRate)
        .join(Job)
        .options(joinedload(JobRate.job))
        .where(*cond)
    )
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
    out: dict[str, Any] = {
        "period_days": days,
        "min_sample": min_sample,
        "lens": lens_name,
        "query_ids": list(query_ids) if query_ids else None,
        "countries": codes or None,
        "jobs_with_rates": len(rows),
        "disclaimer": "Observed published rates in DB only; missing rates stay NULL and are excluded.",
        "items": items,
        **evidence_meta(min_evidence=tier, excluded_thin_n=excluded_thin_n),
    }
    if lens_name == "compare":
        out.update(
            compare_counts(
                db, query_ids=query_ids, days=days, country_code=country_code
            )
        )
    return out
