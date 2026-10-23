"""Temporal median series of advertised JobRate.amount_min (Relations)."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from statistics import median
from typing import Any, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.evidence_gate import (
    DEFAULT_MIN_EVIDENCE,
    evidence_meta,
)
from app.analytics.series import (
    Grain,
    bucket_label_for_date,
    choose_grain,
    corpus_setup,
    iter_bucket_labels,
)
from app.storage.models import Job, JobRate

_RATE_SERIES_LIMITS = (
    "Median advertised amount_min by currency/unit; not market wage. "
    "Observed inventory only. Field `count` holds the median for chart reuse. "
    "Buckets with no rates are null."
)


def _series_key(currency: Optional[str], unit: Optional[str]) -> str:
    curr = (currency or "UNK").strip().upper() or "UNK"
    u = (unit or "unknown").strip().lower() or "unknown"
    return f"{curr}/{u}"


def _fill_bucket_medians(
    values: dict[str, float],
    buckets: Sequence[str],
) -> list[dict[str, Any]]:
    return [{"bucket": b, "count": values.get(b)} for b in buckets]


def rate_series(
    db: Session,
    *,
    days: int = 90,
    country_code: Optional[str] = None,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    min_evidence: Optional[str] = DEFAULT_MIN_EVIDENCE,
    top: int = 5,
    grain: Optional[str] = None,
    unit: Optional[str] = None,
    currency: Optional[str] = None,
    min_sample: int = 3,
) -> dict[str, Any]:
    """Median advertised amount_min per time bucket for top currency/unit keys.

    Grouping: ``{CURRENCY}/{unit}`` (e.g. EUR/hour). Optional ``unit`` /
    ``currency`` filters narrow the corpus before top-N selection.
    """
    resolved: Grain = choose_grain(days, grain)
    job_ids, sample_size, excluded_thin_n, tier, date_from, now = corpus_setup(
        db,
        days=days,
        country_code=country_code,
        lens=lens,
        query_ids=query_ids,
        min_evidence=min_evidence,
    )
    if sample_size == 0:
        return {
            "period_days": days,
            "grain": resolved,
            "sample_size": 0,
            "series": [],
            **evidence_meta(min_evidence=tier, excluded_thin_n=excluded_thin_n),
            "limits": _RATE_SERIES_LIMITS,
        }

    cond = [
        JobRate.job_id.in_(job_ids),
        JobRate.amount_min.is_not(None),
        JobRate.rate_type == "advertised",
        Job.published_at.is_not(None),
    ]
    if unit:
        cond.append(JobRate.unit == unit)
    if currency:
        cond.append(JobRate.currency == currency.upper())

    rows = db.execute(
        select(
            JobRate.currency,
            JobRate.unit,
            Job.published_at,
            JobRate.amount_min,
        )
        .select_from(JobRate)
        .join(Job, Job.id == JobRate.job_id)
        .where(*cond)
    ).all()

    # key → bucket → list of amount_min
    key_bucket_vals: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    key_total: dict[str, int] = defaultdict(int)

    for curr, u, published_at, amount_min in rows:
        if amount_min is None:
            continue
        if isinstance(published_at, datetime):
            d = published_at.date()
        elif isinstance(published_at, date):
            d = published_at
        else:
            continue
        key = _series_key(curr, u)
        label = bucket_label_for_date(d, resolved)
        key_bucket_vals[key][label].append(float(amount_min))
        key_total[key] += 1

    eligible = {
        k: n for k, n in key_total.items() if n >= max(1, min_sample)
    }
    top_keys = [
        k
        for k, _ in sorted(eligible.items(), key=lambda x: (-x[1], x[0]))[
            : max(1, top)
        ]
    ]
    buckets = iter_bucket_labels(date_from.date(), now.date(), resolved)
    series = []
    for key in top_keys:
        medians: dict[str, float] = {}
        for label, vals in key_bucket_vals[key].items():
            if vals:
                medians[label] = float(median(vals))
        series.append(
            {"key": key, "points": _fill_bucket_medians(medians, buckets)}
        )

    return {
        "period_days": days,
        "grain": resolved,
        "sample_size": sample_size,
        "series": series,
        **evidence_meta(min_evidence=tier, excluded_thin_n=excluded_thin_n),
        "limits": _RATE_SERIES_LIMITS,
    }
