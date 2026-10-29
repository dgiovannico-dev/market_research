"""Certifications × country (observed mentions) for map + per-country top-N."""

from __future__ import annotations

from collections import defaultdict
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
from app.analytics.lenses import parse_lens, resolve_job_id_subquery
from app.core.config import get_settings
from app.storage.models import Certification, Job, JobCertification


def certifications_by_country(
    db: Session,
    *,
    days: int = 90,
    country_code: Optional[str] = None,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    min_evidence: Optional[str] = DEFAULT_MIN_EVIDENCE,
    top_n_per_country: int = 5,
    top_countries: int = 40,
) -> dict[str, Any]:
    """Rank certifications within each ISO country (ADR-001 observed counts)."""
    lens_name = parse_lens(lens)
    job_id_subq = resolve_job_id_subquery(db, lens_name, query_ids)
    codes = parse_country_codes(country_code)
    tier = parse_min_evidence(min_evidence)
    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=days)

    corpus_all = base_job_query(
        date_from=date_from,
        country_codes=codes,
        job_id_subq=job_id_subq,
        min_evidence=None,
    )
    excluded_thin_n = count_thin_in_query(db, corpus_all) if tier == "standard" else 0
    corpus = base_job_query(
        date_from=date_from,
        country_codes=codes,
        job_id_subq=job_id_subq,
        min_evidence=tier,
    )
    job_id_sub = corpus.with_only_columns(Job.id).subquery()
    job_ids = select(job_id_sub.c.id)
    sample_size = int(db.scalar(select(func.count()).select_from(job_id_sub)) or 0)

    empty = {
        "lens": lens_name,
        "query_ids": list(query_ids) if query_ids else None,
        "period_days": days,
        "sample_size": sample_size,
        "map_items": [],
        "unknown_jobs": 0,
        "countries": [],
        "disclaimer": (
            "Counts are observed certification mentions in stored job text by country_code, "
            "not market size."
        ),
        **evidence_meta(min_evidence=tier, excluded_thin_n=excluded_thin_n),
    }
    if sample_size == 0:
        return empty

    # Distinct jobs with ≥1 cert, by country (for choropleth).
    jobs_with_cert = db.execute(
        select(Job.country_code, func.count(func.distinct(JobCertification.job_id)))
        .select_from(JobCertification)
        .join(Job, Job.id == JobCertification.job_id)
        .where(JobCertification.job_id.in_(job_ids))
        .group_by(Job.country_code)
    ).all()

    jobs_by_cc: dict[str, int] = {}
    unknown_jobs = 0
    for cc, n in jobs_with_cert:
        country = (cc or "unknown").strip().upper() or "unknown"
        cnt = int(n)
        if country == "UNKNOWN" or country == "unknown":
            unknown_jobs += cnt
            continue
        jobs_by_cc[country] = jobs_by_cc.get(country, 0) + cnt

    name_key = func.lower(Certification.display_name)
    cell_rows = db.execute(
        select(
            Job.country_code,
            func.min(Certification.display_name),
            func.min(Certification.slug),
            func.count(func.distinct(JobCertification.job_id)),
        )
        .select_from(JobCertification)
        .join(Certification, Certification.id == JobCertification.certification_id)
        .join(Job, Job.id == JobCertification.job_id)
        .where(JobCertification.job_id.in_(job_ids))
        .group_by(Job.country_code, name_key)
    ).all()

    per_country: dict[str, list[tuple[str, str, int]]] = defaultdict(list)
    for cc, name, slug, cnt in cell_rows:
        country = (cc or "unknown").strip().upper() or "unknown"
        if country in {"UNKNOWN", "unknown"}:
            continue
        per_country[country].append((str(name), str(slug), int(cnt)))

    ranked_countries = sorted(
        jobs_by_cc.items(), key=lambda x: (-x[1], x[0])
    )[: max(1, min(int(top_countries), 100))]
    per_n = max(1, min(int(top_n_per_country), 20))

    countries_out: list[dict[str, Any]] = []
    for cc, jobs_n in ranked_countries:
        rows = sorted(per_country.get(cc, []), key=lambda x: (-x[2], x[0]))[:per_n]
        top = [
            {
                "certification": name,
                "slug": slug,
                "job_mentions": mentions,
                "evidence_kind": "observed",
            }
            for name, slug, mentions in rows
        ]
        lead = top[0] if top else None
        countries_out.append(
            {
                "country_code": cc,
                "jobs_with_certs": jobs_n,
                "top_certification": lead["certification"] if lead else None,
                "top_mentions": lead["job_mentions"] if lead else 0,
                "top": top,
            }
        )

    settings = get_settings()
    return {
        "lens": lens_name,
        "query_ids": list(query_ids) if query_ids else None,
        "period_days": days,
        "sample_size": sample_size,
        "map_items": [
            {"country_code": cc, "jobs": n} for cc, n in ranked_countries if n > 0
        ],
        "unknown_jobs": unknown_jobs,
        "countries": countries_out,
        "definition": (
            "Per ISO country_code: distinct open jobs with ≥1 extracted certification, "
            "plus top certifications by distinct job mentions."
        ),
        "limits": (
            "Countries with no extracted certs omitted. Unknown country excluded from map. "
            "Thin samples make rankings unstable."
        ),
        "evidence_kind": "extracted",
        "methodology_version": settings.methodology_version,
        "disclaimer": empty["disclaimer"],
        **evidence_meta(min_evidence=tier, excluded_thin_n=excluded_thin_n),
    }
