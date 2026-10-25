"""Rate slice for a single technology (NULL when sample too thin)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.country_filter import parse_country_codes
from app.analytics.evidence_gate import DEFAULT_MIN_EVIDENCE, parse_min_evidence
from app.analytics.job_query import base_job_query
from app.analytics.lenses import parse_lens, resolve_job_id_subquery
from app.analytics.rates import _percentile
from app.storage.models import Job, JobRate, JobSkill, Technology

_DEFAULT_N_MIN = 5


def rate_for_technology(
    db: Session,
    *,
    technology: str,
    days: int = 180,
    country_code: Optional[str] = None,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    min_evidence: Optional[str] = DEFAULT_MIN_EVIDENCE,
    min_sample: int = _DEFAULT_N_MIN,
) -> dict[str, Any]:
    """Observed advertised rates for jobs mentioning ``technology``.

    Returns percentiles when ``n >= min_sample``; otherwise ``rate=None`` with
    ``insufficient_data`` (never invent amounts).
    """
    tech = (technology or "").strip()
    if not tech:
        return {
            "technology": technology,
            "sample_size": 0,
            "rate": None,
            "status": "insufficient_data",
            "limits": "No technology name provided.",
        }

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
        min_evidence=tier,
    )
    job_ids = select(corpus.with_only_columns(Job.id).subquery().c.id)
    tech_job_ids = (
        select(JobSkill.job_id)
        .join(Technology, Technology.id == JobSkill.technology_id)
        .where(
            JobSkill.job_id.in_(job_ids),
            Technology.canonical_name == tech,
        )
    )
    rates = db.scalars(
        select(JobRate).where(
            JobRate.job_id.in_(tech_job_ids),
            JobRate.amount_min.is_not(None),
            JobRate.rate_type == "advertised",
        )
    ).all()
    amounts: list[float] = []
    for rate in rates:
        vals = [v for v in [rate.amount_min, rate.amount_max] if v is not None]
        if not vals:
            continue
        amounts.append(sum(vals) / len(vals))

    n = len(amounts)
    if n < max(1, int(min_sample)):
        return {
            "technology": tech,
            "sample_size": n,
            "rate": None,
            "status": "insufficient_data",
            "n_min": min_sample,
            "limits": (
                f"Observed rates for {tech}: n={n} < n_min={min_sample}. "
                "No percentile invented."
            ),
            "evidence_kind": "derived",
        }

    sorted_amts = sorted(amounts)
    return {
        "technology": tech,
        "sample_size": n,
        "status": "ok",
        "n_min": min_sample,
        "rate": {
            "median": _percentile(sorted_amts, 0.5),
            "p25": _percentile(sorted_amts, 0.25),
            "p75": _percentile(sorted_amts, 0.75),
        },
        "limits": "Advertised amounts in ads mentioning this skill — not earnings guarantee.",
        "evidence_kind": "derived",
    }
