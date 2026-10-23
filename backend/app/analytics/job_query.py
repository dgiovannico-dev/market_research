"""Shared Job select builders for analytics KPIs."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import Select, select

from app.analytics.country_filter import country_codes_clause, parse_country_codes
from app.analytics.evidence_gate import evidence_tier_clause
from app.storage.enums import CLOSED_JOB_STATUSES
from app.storage.models import Job, JobSkill

# Re-export for analytics callers; canonical definition is storage.enums.
_CLOSED_STATUSES = CLOSED_JOB_STATUSES


def base_job_query(
    *,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    country_code: Optional[str] = None,
    country_codes: Optional[Sequence[str]] = None,
    contract_type: Optional[str] = None,
    remote_type: Optional[str] = None,
    technology_id: Optional[int] = None,
    seniority: Optional[str] = None,
    source_id: Optional[int] = None,
    verified_contract_only: bool = False,
    job_id_subq: Optional[Select] = None,
    include_closed: bool = False,
    min_evidence: Optional[str] = None,
) -> Select:
    q = select(Job).where(Job.is_canonical.is_(True))
    if not include_closed:
        q = q.where(Job.status.notin_(_CLOSED_STATUSES))
    tier = evidence_tier_clause(min_evidence)
    if tier is not None:
        q = q.where(tier)
    if date_from:
        q = q.where(Job.published_at >= date_from)
    if date_to:
        q = q.where(Job.published_at <= date_to)
    codes = (
        parse_country_codes(list(country_codes))
        if country_codes is not None
        else parse_country_codes(country_code)
    )
    clause = country_codes_clause(codes)
    if clause is not None:
        q = q.where(clause)
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
    if job_id_subq is not None:
        q = q.where(Job.id.in_(job_id_subq))
    return q
