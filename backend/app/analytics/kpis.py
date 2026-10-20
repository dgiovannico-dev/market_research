from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.storage.models import Job, JobRate, JobSkill, Source, Technology


def _base_job_query(
    *,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    country_code: Optional[str] = None,
    contract_type: Optional[str] = None,
    remote_type: Optional[str] = None,
    technology_id: Optional[int] = None,
    seniority: Optional[str] = None,
    source_id: Optional[int] = None,
    verified_contract_only: bool = False,
) -> Select:
    q = select(Job).where(Job.is_canonical.is_(True))
    if date_from:
        q = q.where(Job.published_at >= date_from)
    if date_to:
        q = q.where(Job.published_at <= date_to)
    if country_code and country_code != "ALL":
        q = q.where(Job.country_code == country_code)
    if contract_type and contract_type != "ALL":
        q = q.where(Job.contract_type == contract_type)
    if remote_type and remote_type != "ALL":
        q = q.where(Job.remote_type == remote_type)
    if seniority:
        q = q.where(Job.seniority == seniority)
    if source_id:
        q = q.where(Job.source_id == source_id)
    if verified_contract_only:
        q = q.where(
            Job.contract_type.in_(["freelance", "b2b", "contractor"]),
            Job.contract_type_confidence.is_not(None),
            Job.contract_type_confidence >= 0.7,
        )
    if technology_id:
        q = q.join(JobSkill).where(JobSkill.technology_id == technology_id)
    return q


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


def dashboard_summary(
    db: Session,
    *,
    days: int = 30,
    country_code: Optional[str] = None,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=days)
    prev_from = date_from - timedelta(days=days)

    current_q = _base_job_query(date_from=date_from, date_to=now, country_code=country_code)
    prev_q = _base_job_query(date_from=prev_from, date_to=date_from, country_code=country_code)

    unique_jobs = db.scalar(select(func.count()).select_from(current_q.subquery())) or 0
    prev_jobs = db.scalar(select(func.count()).select_from(prev_q.subquery())) or 0

    freelance_q = _base_job_query(
        date_from=date_from,
        date_to=now,
        country_code=country_code,
        verified_contract_only=True,
    )
    freelance_verified = db.scalar(select(func.count()).select_from(freelance_q.subquery())) or 0

    with_rate = db.scalar(
        select(func.count(func.distinct(JobRate.job_id)))
        .select_from(JobRate)
        .join(Job)
        .where(
            Job.is_canonical.is_(True),
            Job.published_at >= date_from,
            Job.published_at <= now,
        )
    ) or 0

    remote_count = db.scalar(
        select(func.count()).select_from(
            _base_job_query(
                date_from=date_from, date_to=now, country_code=country_code, remote_type="remote"
            ).subquery()
        )
    ) or 0

    growth = None
    growth_status = "ok"
    if prev_jobs == 0:
        growth_status = "insufficient_data"
    else:
        growth = ((unique_jobs - prev_jobs) / prev_jobs) * 100.0

    # Top technologies
    tech_rows = db.execute(
        select(Technology.canonical_name, func.count(JobSkill.id))
        .join(JobSkill, JobSkill.technology_id == Technology.id)
        .join(Job, Job.id == JobSkill.job_id)
        .where(Job.is_canonical.is_(True), Job.published_at >= date_from, Job.published_at <= now)
        .group_by(Technology.canonical_name)
        .order_by(func.count(JobSkill.id).desc())
        .limit(10)
    ).all()

    country_rows = db.execute(
        select(Job.country_code, func.count(Job.id))
        .where(Job.is_canonical.is_(True), Job.published_at >= date_from, Job.published_at <= now)
        .group_by(Job.country_code)
        .order_by(func.count(Job.id).desc())
        .limit(10)
    ).all()

    sources = db.scalars(select(Source)).all()
    last_success = max((s.last_success_at for s in sources if s.last_success_at), default=None)

    return {
        "period_days": days,
        "generated_at": now.isoformat(),
        "disclaimer": (
            "Counts reflect observed, deduplicated records in this database from configured "
            "sources/imports. They are not estimates of total market size."
        ),
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


def list_jobs(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 50,
    country_code: Optional[str] = None,
    contract_type: Optional[str] = None,
    remote_type: Optional[str] = None,
    technology: Optional[str] = None,
    q: Optional[str] = None,
) -> dict[str, Any]:
    query = _base_job_query(
        country_code=country_code,
        contract_type=contract_type,
        remote_type=remote_type,
    ).options(joinedload(Job.source), joinedload(Job.skills).joinedload(JobSkill.technology), joinedload(Job.rates))
    if technology:
        query = query.join(JobSkill).join(Technology).where(Technology.canonical_name == technology)
    if q:
        like = f"%{q}%"
        query = query.where(
            or_(
                Job.title_original.ilike(like),
                Job.company_original.ilike(like),
                Job.description_original.ilike(like),
            )
        )
    total = db.scalar(select(func.count()).select_from(query.order_by(None).subquery())) or 0
    rows = db.scalars(query.order_by(Job.published_at.desc().nullslast()).offset(skip).limit(limit)).unique().all()
    items = []
    for job in rows:
        items.append(
            {
                "id": job.id,
                "title": job.title_original,
                "company": job.company_original,
                "source": job.source.name if job.source else None,
                "country_code": job.country_code,
                "published_at": job.published_at.isoformat() if job.published_at else None,
                "contract_type": job.contract_type,
                "contract_evidence_kind": job.contract_evidence_kind,
                "contract_type_confidence": job.contract_type_confidence,
                "remote_type": job.remote_type,
                "seniority": job.seniority,
                "residence_restriction": job.residence_restriction,
                "status": job.status,
                "canonical_url": job.canonical_url,
                "technologies": [
                    {
                        "name": s.technology.canonical_name,
                        "importance": s.importance,
                        "evidence_kind": s.evidence_kind,
                        "confidence": s.confidence,
                    }
                    for s in job.skills
                ],
                "rates": [
                    {
                        "amount_min": r.amount_min,
                        "amount_max": r.amount_max,
                        "currency": r.currency,
                        "unit": r.unit,
                        "rate_type": r.rate_type,
                        "evidence_kind": r.evidence_kind,
                        "confidence": r.confidence,
                    }
                    for r in job.rates
                ],
            }
        )
    return {"total": total, "skip": skip, "limit": limit, "items": items}


def technology_trends(db: Session, *, days: int = 90, min_support: int = 3) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=days)
    mid = now - timedelta(days=days // 2)
    recent = db.execute(
        select(Technology.canonical_name, Technology.category, func.count(JobSkill.id))
        .join(JobSkill)
        .join(Job)
        .where(Job.is_canonical.is_(True), Job.published_at >= mid, Job.published_at <= now)
        .group_by(Technology.canonical_name, Technology.category)
    ).all()
    earlier = db.execute(
        select(Technology.canonical_name, func.count(JobSkill.id))
        .join(JobSkill)
        .join(Job)
        .where(Job.is_canonical.is_(True), Job.published_at >= date_from, Job.published_at < mid)
        .group_by(Technology.canonical_name)
    ).all()
    earlier_map = {name: count for name, count in earlier}
    items = []
    for name, category, recent_count in recent:
        prev = earlier_map.get(name, 0)
        total = recent_count + prev
        if total < min_support:
            growth = None
            status = "insufficient_data"
        elif prev == 0:
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
    return {"period_days": days, "min_support": min_support, "items": items}


def data_quality_report(db: Session) -> dict[str, Any]:
    total = db.scalar(select(func.count()).select_from(Job).where(Job.is_canonical.is_(True))) or 0
    if total == 0:
        return {
            "total_canonical_jobs": 0,
            "metrics": {},
            "sources": [],
            "disclaimer": "No jobs ingested yet.",
        }

    def pct(n: int) -> float:
        return round((n / total) * 100.0, 2)

    with_date = db.scalar(
        select(func.count()).select_from(Job).where(Job.is_canonical.is_(True), Job.published_at.is_not(None))
    ) or 0
    known_country = db.scalar(
        select(func.count())
        .select_from(Job)
        .where(Job.is_canonical.is_(True), Job.country_code != "unknown")
    ) or 0
    known_contract = db.scalar(
        select(func.count())
        .select_from(Job)
        .where(Job.is_canonical.is_(True), Job.contract_type != "unknown")
    ) or 0
    with_rate = db.scalar(select(func.count(func.distinct(JobRate.job_id)))) or 0
    duplicates = db.scalar(select(func.count()).select_from(Job).where(Job.is_canonical.is_(False))) or 0
    sources = db.scalars(select(Source)).all()
    return {
        "total_canonical_jobs": total,
        "metrics": {
            "pct_with_valid_date": pct(with_date),
            "pct_known_country": pct(known_country),
            "pct_known_contract": pct(known_contract),
            "pct_with_rate": pct(with_rate),
            "duplicate_non_canonical_count": duplicates,
        },
        "sources": [
            {
                "id": s.id,
                "name": s.name,
                "connector_status": s.connector_status,
                "enabled": s.enabled,
                "last_success_at": s.last_success_at.isoformat() if s.last_success_at else None,
                "last_error": s.last_error,
                "coverage_notes": s.coverage_notes,
            }
            for s in sources
        ],
        "disclaimer": "Quality metrics describe this database, not the external market.",
    }
