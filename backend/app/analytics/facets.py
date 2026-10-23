"""Observed facet mixes (remote, contract, seniority, status) for dashboard charts."""

from __future__ import annotations

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

_FACET_FIELDS = (
    ("remote_type", "remote"),
    ("contract_type", "contract"),
    ("seniority", "seniority"),
    ("status", "status"),
)


def _bucket_counts(db: Session, job_q, column: str) -> list[dict[str, Any]]:
    subq = job_q.subquery()
    col = getattr(subq.c, column)
    bucket = func.coalesce(col, "unknown").label("bucket")
    rows = db.execute(
        select(bucket, func.count())
        .select_from(subq)
        .group_by(bucket)
        .order_by(func.count().desc())
    ).all()
    return [
        {"key": (key or "unknown"), "jobs": int(n)}
        for key, n in rows
        if n
    ]


def market_facets(
    db: Session,
    *,
    days: int = 30,
    country_code: Optional[str] = None,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    min_evidence: Optional[str] = DEFAULT_MIN_EVIDENCE,
) -> dict[str, Any]:
    lens_name = parse_lens(lens)
    if lens_name == "compare":
        market = market_facets(
            db,
            days=days,
            country_code=country_code,
            lens="market",
            query_ids=query_ids,
            min_evidence=min_evidence,
        )
        focus = market_facets(
            db,
            days=days,
            country_code=country_code,
            lens="focus",
            query_ids=query_ids,
            min_evidence=min_evidence,
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
    sample_size = int(db.scalar(select(func.count()).select_from(job_q.subquery())) or 0)
    facets: dict[str, list[dict[str, Any]]] = {}
    for column, name in _FACET_FIELDS:
        facets[name] = _bucket_counts(db, job_q, column)

    settings = get_settings()
    return {
        "lens": lens_name,
        "query_ids": list(query_ids) if query_ids else None,
        "countries": codes or None,
        "period_days": days,
        "sample_size": sample_size,
        "facets": facets,
        "definition": (
            "Observed counts of classified fields among canonical open jobs in period. "
            "Unknown means missing or unclassified."
        ),
        "limits": (
            "Not a census of the labour market. Shares sum to sample_size for each facet. "
            "Seniority is often sparse."
        ),
        "evidence_kind": "derived",
        "methodology_version": settings.methodology_version,
        "disclaimer": (
            "Counts reflect observed, deduplicated records in this database from configured "
            "sources/imports. They are not estimates of total market size."
        ),
        **evidence_meta(min_evidence=tier, excluded_thin_n=excluded_thin_n),
    }
