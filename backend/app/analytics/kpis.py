from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.analytics.country_filter import country_codes_clause, parse_country_codes
from app.analytics.coverage_notes import attach_coverage_notes, coverage_notes_for_slice
from app.analytics.evidence_gate import (
    DEFAULT_MIN_EVIDENCE,
    count_thin_in_query,
    evidence_meta,
    parse_min_evidence,
)
from app.analytics.job_query import base_job_query
from app.analytics.jobs_daily import jobs_per_day_series
from app.analytics.jobs_list import list_jobs
from app.analytics.lenses import compare_counts, parse_lens, resolve_job_id_subquery
from app.analytics.quality import data_quality_report
from app.core.config import get_settings
from app.storage.enums import JobStatus
from app.storage.models import Job, JobRate, JobSkill, Source, Technology

_CLOSED = (
    JobStatus.closed.value,
    JobStatus.closed_stale.value,
    JobStatus.removed_from_source.value,
)

__all__ = [
    "dashboard_summary",
    "list_jobs",
    "technology_trends",
    "data_quality_report",
]


def _metric(
    name: str,
    value: float,
    *,
    numerator: float | None = None,
    denominator: float | None = None,
    sample_size: int = 0,
    definition: str,
    unit: str = "count",
    limits: str,
    evidence_kind: str = "derived",
) -> dict[str, Any]:
    settings = get_settings()
    return {
        "metric_name": name,
        "metric_value": value,
        "numerator": numerator if numerator is not None else value,
        "denominator": denominator,
        "sample_size": sample_size,
        "unit": unit,
        "definition": definition,
        "source_coverage": "Observed jobs currently stored from enabled connectors/imports only. "
        "Not a census of the full market.",
        "methodology_version": settings.methodology_version,
        "evidence_kind": evidence_kind,
        "limits": limits,
    }


def _lens_where(job_id_subq: Optional[Select]):
    return (Job.id.in_(job_id_subq),) if job_id_subq is not None else ()


def _clamp_top_n(top_n: int) -> int:
    return max(1, min(int(top_n), 100))


def dashboard_summary(
    db: Session,
    *,
    days: int = 30,
    country_code: Optional[str] = None,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    top_n: int = 100,
) -> dict[str, Any]:
    """Dashboard KPIs. ``lens=None`` = all jobs; pass ``market`` for Demand Compass.

    ``top_n`` (1–100, default 100) caps ``top_technologies`` and ``top_countries``.
    """
    top_n = _clamp_top_n(top_n)
    lens_name = parse_lens(lens)
    codes = parse_country_codes(country_code)
    country_clause = country_codes_clause(codes)
    if lens_name == "compare":
        counts = compare_counts(
            db, query_ids=query_ids, days=days, country_code=country_code
        )
        market = dashboard_summary(
            db,
            days=days,
            country_code=country_code,
            lens="market",
            query_ids=query_ids,
            top_n=top_n,
        )
        focus = dashboard_summary(
            db,
            days=days,
            country_code=country_code,
            lens="focus",
            query_ids=query_ids,
            top_n=top_n,
        )
        # Lift shared / market-side fields so clients can read top-level without
        # special-casing compare (sources / period are not lens-split; guided UI
        # still expects kpis / growth_status / top_* at the root).
        return {
            "lens": "compare",
            "query_ids": list(query_ids) if query_ids else None,
            "countries": codes or None,
            **counts,
            "period_days": market.get("period_days", days),
            "generated_at": market.get("generated_at"),
            "disclaimer": market.get("disclaimer"),
            "growth_status": market.get("growth_status"),
            "kpis": market.get("kpis") or [],
            "jobs_per_day": market.get("jobs_per_day") or [],
            "top_technologies": market.get("top_technologies") or [],
            "top_countries": market.get("top_countries") or [],
            "data_quality": market.get("data_quality"),
            "coverage_notes": market.get("coverage_notes") or [],
            "market": market,
            "focus": focus,
        }

    job_id_subq = resolve_job_id_subquery(db, lens_name, query_ids)
    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=days)
    prev_from = date_from - timedelta(days=days)

    current_q = base_job_query(
        date_from=date_from, date_to=now, country_codes=codes, job_id_subq=job_id_subq
    )
    prev_q = base_job_query(
        date_from=prev_from, date_to=date_from, country_codes=codes, job_id_subq=job_id_subq
    )

    unique_jobs = db.scalar(select(func.count()).select_from(current_q.subquery())) or 0
    prev_jobs = db.scalar(select(func.count()).select_from(prev_q.subquery())) or 0

    freelance_q = base_job_query(
        date_from=date_from,
        date_to=now,
        country_codes=codes,
        verified_contract_only=True,
        job_id_subq=job_id_subq,
    )
    freelance_verified = db.scalar(select(func.count()).select_from(freelance_q.subquery())) or 0

    rate_conds = [
        Job.is_canonical.is_(True),
        Job.published_at >= date_from,
        Job.published_at <= now,
        *_lens_where(job_id_subq),
    ]
    if country_clause is not None:
        rate_conds.append(country_clause)
    with_rate = (
        db.scalar(
            select(func.count(func.distinct(JobRate.job_id)))
            .select_from(JobRate)
            .join(Job)
            .where(*rate_conds)
        )
        or 0
    )

    remote_count = (
        db.scalar(
            select(func.count()).select_from(
                base_job_query(
                    date_from=date_from,
                    date_to=now,
                    country_codes=codes,
                    remote_type="remote",
                    job_id_subq=job_id_subq,
                ).subquery()
            )
        )
        or 0
    )

    growth = None
    growth_status = "ok"
    if prev_jobs == 0:
        growth_status = "insufficient_data"
    else:
        growth = ((unique_jobs - prev_jobs) / prev_jobs) * 100.0

    tech_conds = [
        Job.is_canonical.is_(True),
        Job.published_at >= date_from,
        Job.published_at <= now,
        *_lens_where(job_id_subq),
    ]
    if country_clause is not None:
        tech_conds.append(country_clause)
    tech_rows = db.execute(
        select(Technology.canonical_name, func.count(JobSkill.id))
        .join(JobSkill, JobSkill.technology_id == Technology.id)
        .join(Job, Job.id == JobSkill.job_id)
        .where(*tech_conds)
        .group_by(Technology.canonical_name)
        .order_by(func.count(JobSkill.id).desc())
        .limit(top_n)
    ).all()

    country_conds = [
        Job.is_canonical.is_(True),
        Job.published_at >= date_from,
        Job.published_at <= now,
        *_lens_where(job_id_subq),
    ]
    if country_clause is not None:
        country_conds.append(country_clause)
    country_rows = db.execute(
        select(Job.country_code, func.count(Job.id))
        .where(*country_conds)
        .group_by(Job.country_code)
        .order_by(func.count(Job.id).desc())
        .limit(top_n)
    ).all()

    sources = db.scalars(select(Source)).all()
    last_success = max((s.last_success_at for s in sources if s.last_success_at), default=None)

    jobs_per_day = (
        jobs_per_day_series(
            db,
            date_from=date_from,
            date_to=now,
            country_codes=codes,
            job_id_subq=job_id_subq,
        )
        if unique_jobs
        else []
    )

    out = {
        "period_days": days,
        "lens": lens_name,
        "query_ids": list(query_ids) if query_ids else None,
        "countries": codes or None,
        "generated_at": now.isoformat(),
        "disclaimer": (
            "Counts reflect observed, deduplicated records in this database from configured "
            "sources/imports. They are not estimates of total market size."
        ),
        "jobs_per_day": jobs_per_day,
        "kpis": [
            _metric(
                "unique_jobs_observed",
                float(unique_jobs),
                sample_size=unique_jobs,
                definition="Canonical (deduplicated) jobs with published_at in period.",
                limits="Depends on active connectors, queries and import coverage.",
            ),
            _metric(
                "freelance_b2b_verified",
                float(freelance_verified),
                numerator=float(freelance_verified),
                denominator=float(unique_jobs) if unique_jobs else None,
                sample_size=unique_jobs,
                definition="Jobs classified freelance/b2b/contractor with confidence >= 0.7.",
                limits="Classification is extracted/inferred from text; not manually verified by default.",
            ),
            _metric(
                "observed_demand_growth_pct",
                float(growth) if growth is not None else 0.0,
                numerator=float(unique_jobs),
                denominator=float(prev_jobs) if prev_jobs else None,
                sample_size=unique_jobs + prev_jobs,
                unit="percent",
                definition="Percent change vs previous equal-length window of observed unique jobs.",
                limits=(
                    "insufficient_data"
                    if growth_status == "insufficient_data"
                    else "Sensitive to source/query changes; not market growth."
                ),
                evidence_kind="derived",
            ),
            _metric(
                "jobs_with_published_rate",
                float(with_rate),
                sample_size=unique_jobs,
                definition="Jobs with at least one extracted/advertised rate record.",
                limits="Many sources omit rates; NULL rates are not treated as zero.",
            ),
            _metric(
                "remote_jobs_observed",
                float(remote_count),
                sample_size=unique_jobs,
                definition="Jobs classified remote_type=remote.",
                limits="Remote != acceptance of Italian residents.",
            ),
        ],
        "top_technologies": [
            {"technology": name, "job_skill_mentions": count, "evidence_kind": "derived"}
            for name, count in tech_rows
        ],
        "top_countries": [
            {"country_code": code, "jobs": count, "evidence_kind": "derived"}
            for code, count in country_rows
        ],
        "data_quality": {
            "sources_total": len(sources),
            "sources_enabled": sum(1 for s in sources if s.enabled),
            "sources_with_errors": sum(1 for s in sources if s.last_error),
            "last_source_success_at": last_success.isoformat() if last_success else None,
        },
        "growth_status": growth_status,
    }
    notes = coverage_notes_for_slice(
        db, country_code=country_code, job_id_subq=job_id_subq, date_from=date_from
    )
    return attach_coverage_notes(out, notes)


def technology_trends(
    db: Session,
    *,
    days: int = 90,
    min_support: int = 3,
    country_code: Optional[str] = None,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    min_evidence: Optional[str] = DEFAULT_MIN_EVIDENCE,
) -> dict[str, Any]:
    """Technology half-period trends. ``lens=None`` = all jobs."""
    lens_name = parse_lens(lens)
    codes = parse_country_codes(country_code)
    country_clause = country_codes_clause(codes)
    tier = parse_min_evidence(min_evidence)
    if lens_name == "compare":
        counts = compare_counts(
            db, query_ids=query_ids, days=days, country_code=country_code
        )
        market = technology_trends(
            db,
            days=days,
            min_support=min_support,
            country_code=country_code,
            lens="market",
            query_ids=query_ids,
            min_evidence=min_evidence,
        )
        focus = technology_trends(
            db,
            days=days,
            min_support=min_support,
            country_code=country_code,
            lens="focus",
            query_ids=query_ids,
            min_evidence=min_evidence,
        )
        # Lift shared metadata (period / evidence) like dashboard_summary.compare.
        return {
            "lens": "compare",
            "query_ids": list(query_ids) if query_ids else None,
            "countries": codes or None,
            **counts,
            "period_days": market.get("period_days", days),
            "min_support": market.get("min_support", min_support),
            "min_evidence": market.get("min_evidence"),
            "excluded_thin_n": market.get("excluded_thin_n", 0),
            "market": market,
            "focus": focus,
        }

    job_id_subq = resolve_job_id_subquery(db, lens_name, query_ids)
    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=days)
    mid = now - timedelta(days=days // 2)
    corpus_all = base_job_query(
        date_from=date_from,
        country_codes=codes,
        job_id_subq=job_id_subq,
        min_evidence=None,
    )
    excluded_thin_n = count_thin_in_query(db, corpus_all) if tier == "standard" else 0
    recent_conds = [
        Job.is_canonical.is_(True),
        Job.status.notin_(_CLOSED),
        Job.published_at >= mid,
        Job.published_at <= now,
        *_lens_where(job_id_subq),
    ]
    earlier_conds = [
        Job.is_canonical.is_(True),
        Job.status.notin_(_CLOSED),
        Job.published_at >= date_from,
        Job.published_at < mid,
        *_lens_where(job_id_subq),
    ]
    if country_clause is not None:
        recent_conds.append(country_clause)
        earlier_conds.append(country_clause)
    if tier:
        recent_conds.append(Job.evidence_tier == tier)
        earlier_conds.append(Job.evidence_tier == tier)
    recent = db.execute(
        select(Technology.canonical_name, Technology.category, func.count(JobSkill.id))
        .join(JobSkill)
        .join(Job)
        .where(*recent_conds)
        .group_by(Technology.canonical_name, Technology.category)
    ).all()
    earlier = db.execute(
        select(Technology.canonical_name, func.count(JobSkill.id))
        .join(JobSkill)
        .join(Job)
        .where(*earlier_conds)
        .group_by(Technology.canonical_name)
    ).all()
    earlier_map = {name: count for name, count in earlier}
    items = []
    for name, category, recent_count in recent:
        prev = earlier_map.get(name, 0)
        total = recent_count + prev
        if total < min_support or prev == 0:
            growth = None
            status = "insufficient_data"
        else:
            growth = ((recent_count - prev) / prev) * 100.0
            status = "ok"
        items.append(
            {
                "technology": name,
                "category": category,
                "recent_mentions": recent_count,
                "previous_mentions": prev,
                "sample_size": total,
                "growth_pct": growth,
                "status": status,
                "evidence_kind": "derived",
                "limits": "Observed mentions in stored jobs only; co-occurrence != causation.",
            }
        )
    items.sort(key=lambda x: x["recent_mentions"], reverse=True)
    return {
        "period_days": days,
        "min_support": min_support,
        "lens": lens_name,
        "query_ids": list(query_ids) if query_ids else None,
        "countries": codes or None,
        "items": items,
        **evidence_meta(min_evidence=tier, excluded_thin_n=excluded_thin_n),
    }
