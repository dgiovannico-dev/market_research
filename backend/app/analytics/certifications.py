"""Top certifications by observed job mentions (ADR-001, SPEC-certifications)."""

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
from app.storage.models import Certification, Job, JobCertification


def top_certifications(
    db: Session,
    *,
    days: int = 90,
    country_code: Optional[str] = None,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    top_n: int = 20,
    min_evidence: Optional[str] = DEFAULT_MIN_EVIDENCE,
) -> dict[str, Any]:
    lens_name = parse_lens(lens)
    if lens_name == "compare":
        market = top_certifications(
            db,
            days=days,
            country_code=country_code,
            lens="market",
            query_ids=query_ids,
            top_n=top_n,
            min_evidence=min_evidence,
        )
        focus = top_certifications(
            db,
            days=days,
            country_code=country_code,
            lens="focus",
            query_ids=query_ids,
            top_n=top_n,
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
    job_ids = select(job_q.with_only_columns(Job.id).subquery().c.id)
    limit = max(1, min(int(top_n), 100))
    rows = db.execute(
        select(
            Certification.display_name,
            Certification.slug,
            func.count(JobCertification.id),
        )
        .join(JobCertification, JobCertification.certification_id == Certification.id)
        .where(JobCertification.job_id.in_(job_ids))
        .group_by(Certification.id, Certification.display_name, Certification.slug)
        .order_by(func.count(JobCertification.id).desc())
        .limit(limit)
    ).all()
    sample_size = db.scalar(select(func.count()).select_from(job_q.subquery())) or 0
    settings = get_settings()
    return {
        "lens": lens_name,
        "query_ids": list(query_ids) if query_ids else None,
        "countries": codes or None,
        "period_days": days,
        "sample_size": int(sample_size),
        "items": [
            {
                "certification": name,
                "slug": slug,
                "job_mentions": int(count),
                "evidence_kind": "observed",
            }
            for name, slug, count in rows
        ],
        "definition": (
            "Counts of canonical open jobs whose extracted text mentions each "
            "certification (taxonomy aliases). A job may count in multiple certs."
        ),
        "limits": (
            "Missing links mean extract found no alias — not proof that no cert is required."
        ),
        "evidence_kind": "extracted",
        "methodology_version": settings.methodology_version,
        "disclaimer": (
            "Counts are observed certification mentions in stored job text, not market size."
        ),
        **evidence_meta(min_evidence=tier, excluded_thin_n=excluded_thin_n),
    }
