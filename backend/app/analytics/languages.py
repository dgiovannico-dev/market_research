"""Aggregates for Job.language_requirements (human languages in ads)."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.analytics.country_filter import parse_country_codes
from app.analytics.evidence_gate import (
    DEFAULT_MIN_EVIDENCE,
    count_thin_in_query,
    evidence_meta,
    parse_min_evidence,
)
from app.analytics.job_query import base_job_query
from app.analytics.lenses import compare_counts, parse_lens, resolve_job_id_subquery
from app.core.config import get_settings
from app.storage.models import Job


def _normalize_codes(raw: Any) -> list[str]:
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            continue
        code = item.strip().lower()[:8]
        if len(code) >= 2 and code.isalpha():
            out.append(code)
    return out


def language_demand(
    db: Session,
    *,
    days: int = 90,
    country_code: Optional[str] = None,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    min_evidence: Optional[str] = DEFAULT_MIN_EVIDENCE,
    limit: int = 30,
) -> dict[str, Any]:
    lens_name = parse_lens(lens)
    if lens_name == "compare":
        market = language_demand(
            db,
            days=days,
            country_code=country_code,
            lens="market",
            query_ids=query_ids,
            min_evidence=min_evidence,
            limit=limit,
        )
        focus = language_demand(
            db,
            days=days,
            country_code=country_code,
            lens="focus",
            query_ids=query_ids,
            min_evidence=min_evidence,
            limit=limit,
        )
        return {
            "lens": "compare",
            "query_ids": list(query_ids) if query_ids else None,
            "period_days": days,
            **compare_counts(
                db, query_ids=query_ids, days=days, country_code=country_code
            ),
            "market": market,
            "focus": focus,
            "disclaimer": market.get("disclaimer"),
        }

    tier = parse_min_evidence(min_evidence)
    codes = parse_country_codes(country_code)
    job_id_subq = resolve_job_id_subquery(db, lens_name, query_ids)
    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=days)
    corpus = base_job_query(
        date_from=date_from,
        country_codes=codes,
        job_id_subq=job_id_subq,
        min_evidence=None,
    )
    excluded_thin_n = count_thin_in_query(db, corpus) if tier == "standard" else 0
    job_q = base_job_query(
        date_from=date_from,
        country_codes=codes,
        job_id_subq=job_id_subq,
        min_evidence=tier,
    )
    jobs = db.scalars(job_q).all()
    sample_size = len(jobs)
    counter: Counter[str] = Counter()
    with_any = 0
    by_country: dict[str, Counter[str]] = {}
    for job in jobs:
        langs = _normalize_codes(job.language_requirements)
        if not langs:
            continue
        with_any += 1
        for lang in set(langs):
            counter[lang] += 1
            cc = (job.country_code or "unknown").upper()
            by_country.setdefault(cc, Counter())[lang] += 1

    limit = max(1, min(int(limit), 100))
    items = [
        {
            "language": code,
            "jobs": n,
            "share": round(n / sample_size, 4) if sample_size else 0.0,
        }
        for code, n in counter.most_common(limit)
    ]
    settings = get_settings()
    coverage = round(with_any / sample_size, 4) if sample_size else 0.0
    return {
        "lens": lens_name,
        "query_ids": list(query_ids) if query_ids else None,
        "countries": codes or None,
        "period_days": days,
        "sample_size": sample_size,
        "jobs_with_language_requirements": with_any,
        "coverage_pct": coverage,
        "items": items,
        "by_country_top": {
            cc: [{"language": lang, "jobs": n} for lang, n in ctr.most_common(8)]
            for cc, ctr in sorted(by_country.items(), key=lambda x: -sum(x[1].values()))[
                :40
            ]
        },
        "definition": (
            "Counts of canonical open jobs whose language_requirements list includes "
            "each ISO 639-1 code (extracted from posting text). A job may count in multiple languages."
        ),
        "limits": (
            "Missing language_requirements means extraction found none — not proof that no "
            "language is required. Programming languages are excluded by design."
        ),
        "evidence_kind": "extracted",
        "methodology_version": settings.methodology_version,
        "disclaimer": (
            "Observed extraction only. Coverage_pct is the share of jobs with ≥1 detected "
            "human language requirement."
        ),
        **evidence_meta(min_evidence=tier, excluded_thin_n=excluded_thin_n),
    }
