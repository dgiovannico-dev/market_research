"""KPI facades — thin pass-through to analytics (Session remains there)."""

from __future__ import annotations

from typing import Any, Optional, Sequence

from sqlalchemy.orm import Session

from app.analytics import kpis as _kpis
from app.analytics.evidence_gate import DEFAULT_MIN_EVIDENCE


def dashboard_summary(
    db: Session,
    *,
    days: int = 30,
    country_code: Optional[str] = None,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    top_n: int = 100,
) -> dict[str, Any]:
    return _kpis.dashboard_summary(
        db,
        days=days,
        country_code=country_code,
        lens=lens,
        query_ids=query_ids,
        top_n=top_n,
    )


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
    lens: Optional[str] = "market",
    query_ids: Optional[Sequence[int]] = None,
) -> dict[str, Any]:
    return _kpis.list_jobs(
        db,
        skip=skip,
        limit=limit,
        country_code=country_code,
        contract_type=contract_type,
        remote_type=remote_type,
        technology=technology,
        q=q,
        lens=lens or "market",
        query_ids=query_ids,
    )


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
    return _kpis.technology_trends(
        db,
        days=days,
        min_support=min_support,
        country_code=country_code,
        lens=lens,
        query_ids=query_ids,
        min_evidence=min_evidence,
    )


def data_quality_report(
    db: Session,
    *,
    country_code: Optional[str] = None,
    lens: Optional[str] = "market",
    query_ids: Optional[Sequence[int]] = None,
) -> dict[str, Any]:
    return _kpis.data_quality_report(
        db,
        country_code=country_code,
        lens=lens or "market",
        query_ids=query_ids,
    )
