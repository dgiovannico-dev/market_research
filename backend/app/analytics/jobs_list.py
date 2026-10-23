"""Paginated job listing for market analytics (lens-aware)."""

from __future__ import annotations

from typing import Any, Optional, Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.analytics.job_query import base_job_query
from app.analytics.lenses import compare_counts, parse_lens, resolve_job_id_subquery
from app.storage.models import Job, JobSkill, Technology


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
    lens: str = "market",
    query_ids: Optional[Sequence[int]] = None,
) -> dict[str, Any]:
    lens_name = parse_lens(lens)
    job_id_subq = resolve_job_id_subquery(db, lens_name, query_ids)
    query = base_job_query(
        country_code=country_code,
        contract_type=contract_type,
        remote_type=remote_type,
        job_id_subq=job_id_subq,
    ).options(
        joinedload(Job.source),
        joinedload(Job.skills).joinedload(JobSkill.technology),
        joinedload(Job.rates),
    )
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
    rows = (
        db.scalars(query.order_by(Job.published_at.desc().nullslast()).offset(skip).limit(limit))
        .unique()
        .all()
    )
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
                "evidence_tier": getattr(job, "evidence_tier", None) or "standard",
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
    out: dict[str, Any] = {
        "total": total,
        "skip": skip,
        "limit": limit,
        "lens": lens_name,
        "query_ids": list(query_ids) if query_ids else None,
        "items": items,
    }
    if lens_name == "compare":
        out.update(compare_counts(db, query_ids=query_ids, country_code=country_code))
    return out
