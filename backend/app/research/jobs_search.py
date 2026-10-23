"""DB-only job search for Explore (no external crawl)."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import Select, exists, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.analytics.lenses import apply_lens_filter
from app.storage.enums import CLOSED_JOB_STATUSES
from app.storage.models import Job, JobIntentMatch, JobSkill, Source

SORT_COLUMNS = frozenset(
    {"published_at", "title", "company", "country_code", "contract_type", "source"}
)


def parse_csv_values(raw: Optional[str]) -> list[str]:
    if not raw:
        return []
    return [part.strip() for part in str(raw).split(",") if part.strip()]


def parse_csv_ints(raw: Optional[str]) -> list[int]:
    out: list[int] = []
    for part in parse_csv_values(raw):
        try:
            out.append(int(part))
        except ValueError:
            continue
    return out


def apply_research_job_scope(
    db: Session,
    stmt: Select,
    *,
    query_id: Optional[int] = None,
    lens: Optional[str] = None,
) -> Select:
    """Apply lens / query_id scope via shared analytics lenses (Wave 6).

    ``query_id`` stays Explore-specific (exact intent match, any kind).
    ``lens`` delegates to ``apply_lens_filter`` — one implementation with market KPIs.
    """
    if query_id is not None:
        return stmt.where(
            exists(
                select(JobIntentMatch.id).where(
                    JobIntentMatch.job_id == Job.id,
                    JobIntentMatch.query_id == query_id,
                )
            )
        )
    return apply_lens_filter(stmt, db, lens=lens)


def _order_clause(sort: str, order: str):
    direction = (order or "desc").strip().lower()
    asc = direction == "asc"
    col_key = (sort or "published_at").strip().lower()
    if col_key not in SORT_COLUMNS:
        col_key = "published_at"

    if col_key == "title":
        col = Job.title_original
    elif col_key == "company":
        col = Job.company_original
    elif col_key == "country_code":
        col = Job.country_code
    elif col_key == "contract_type":
        col = Job.contract_type
    elif col_key == "source":
        col = Source.name
    else:
        col = Job.published_at

    ordered = col.asc().nullslast() if asc else col.desc().nullslast()
    return col_key, "asc" if asc else "desc", ordered


def search_research_jobs(
    db: Session,
    *,
    q: Optional[str] = None,
    query_id: Optional[int] = None,
    lens: Optional[str] = None,
    country_code: Optional[str] = None,
    source_id: Optional[str] = None,
    contract_type: Optional[str] = None,
    remote_type: Optional[str] = None,
    sort: Optional[str] = None,
    order: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    include_closed: bool = False,
) -> dict[str, Any]:
    """Search canonical jobs from Postgres using JobIntentMatch for lenses."""
    countries = [c.upper() for c in parse_csv_values(country_code)]
    source_ids = parse_csv_ints(source_id)
    contracts = parse_csv_values(contract_type)
    remotes = parse_csv_values(remote_type)
    sort_key, order_key, order_expr = _order_clause(sort or "published_at", order or "desc")

    stmt = select(Job).where(Job.is_canonical.is_(True))
    if not include_closed:
        stmt = stmt.where(Job.status.notin_(CLOSED_JOB_STATUSES))
    stmt = stmt.options(
        joinedload(Job.source),
        joinedload(Job.skills).joinedload(JobSkill.technology),
        joinedload(Job.rates),
    )
    stmt = apply_research_job_scope(db, stmt, query_id=query_id, lens=lens)

    if countries:
        stmt = stmt.where(Job.country_code.in_(countries))
    if source_ids:
        stmt = stmt.where(Job.source_id.in_(source_ids))
    if contracts:
        stmt = stmt.where(Job.contract_type.in_(contracts))
    if remotes:
        stmt = stmt.where(Job.remote_type.in_(remotes))

    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                Job.title_original.ilike(like),
                Job.company_original.ilike(like),
                Job.description_original.ilike(like),
            )
        )

    if sort_key == "source":
        stmt = stmt.outerjoin(Source, Job.source_id == Source.id)

    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    rows = db.scalars(stmt.order_by(order_expr).offset(skip).limit(limit)).unique().all()
    items = [_serialize_job(job) for job in rows]
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "lens": lens,
        "query_id": query_id,
        "q": q,
        "country_code": countries[0] if len(countries) == 1 else None,
        "countries": countries,
        "source_ids": source_ids,
        "contract_types": contracts,
        "remote_types": remotes,
        "sort": sort_key,
        "order": order_key,
        "items": items,
    }


def _serialize_job(job: Job) -> dict[str, Any]:
    return {
        "id": job.id,
        "title": job.title_original,
        "company": job.company_original,
        "source": job.source.name if job.source else None,
        "source_id": job.source_id,
        "country_code": job.country_code,
        "published_at": job.published_at.isoformat() if job.published_at else None,
        "contract_type": job.contract_type,
        "remote_type": job.remote_type,
        "seniority": job.seniority,
        "status": job.status,
        "evidence_tier": getattr(job, "evidence_tier", None) or "standard",
        "canonical_url": job.canonical_url,
        "technologies": [
            {
                "name": s.technology.canonical_name,
                "importance": s.importance,
            }
            for s in job.skills
            if s.technology
        ],
        "rates": [
            {
                "amount_min": r.amount_min,
                "amount_max": r.amount_max,
                "currency": r.currency,
                "unit": r.unit,
            }
            for r in job.rates
        ],
    }
