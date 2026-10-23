"""Lens facades shared by Explore and market analytics."""

from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import Select
from sqlalchemy.orm import Session

from app.analytics.lenses import (
    compare_counts as _compare_counts,
)
from app.analytics.lenses import (
    resolve_job_id_subquery as _resolve_job_id_subquery,
)


def resolve_job_id_subquery(
    db: Session,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    *,
    days: Optional[int] = None,
) -> Optional[Select]:
    return _resolve_job_id_subquery(db, lens, query_ids, days=days)


def compare_counts(
    db: Session,
    *,
    query_ids: Optional[Sequence[int]] = None,
    days: Optional[int] = None,
    country_code: Optional[str] = None,
) -> dict[str, int]:
    return _compare_counts(
        db, query_ids=query_ids, days=days, country_code=country_code
    )
