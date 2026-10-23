"""Observed jobs-per-day series for Executive sparkline (SPEC-dashboard jobs_spark)."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Optional, Sequence

from sqlalchemy import Date, Select, cast, func, select
from sqlalchemy.orm import Session

from app.analytics.country_filter import country_codes_clause, parse_country_codes
from app.storage.models import Job


def fill_daily_counts(
    counts: dict[date, int],
    *,
    start: date,
    end: date,
) -> list[dict[str, Any]]:
    """Build a continuous day → jobs list (zeros for quiet days). Empty if start > end."""
    if start > end:
        return []
    out: list[dict[str, Any]] = []
    cursor = start
    while cursor <= end:
        out.append({"day": cursor.isoformat(), "jobs": int(counts.get(cursor, 0))})
        cursor += timedelta(days=1)
    return out


def jobs_per_day_series(
    db: Session,
    *,
    date_from: datetime,
    date_to: datetime,
    country_code: Optional[str] = None,
    country_codes: Optional[Sequence[str]] = None,
    job_id_subq: Optional[Select] = None,
) -> list[dict[str, Any]]:
    """Canonical jobs counted by ``published_at`` calendar day (UTC date)."""
    day_expr = cast(Job.published_at, Date)
    q = (
        select(day_expr.label("day"), func.count(Job.id))
        .where(
            Job.is_canonical.is_(True),
            Job.published_at.is_not(None),
            Job.published_at >= date_from,
            Job.published_at <= date_to,
        )
        .group_by(day_expr)
        .order_by(day_expr)
    )
    codes = (
        parse_country_codes(list(country_codes))
        if country_codes is not None
        else parse_country_codes(country_code)
    )
    clause = country_codes_clause(codes)
    if clause is not None:
        q = q.where(clause)
    if job_id_subq is not None:
        q = q.where(Job.id.in_(job_id_subq))

    rows = db.execute(q).all()
    counts: dict[date, int] = {}
    for day_val, count in rows:
        if day_val is None:
            continue
        if isinstance(day_val, datetime):
            d = day_val.date()
        else:
            d = day_val
        counts[d] = int(count)

    series = fill_daily_counts(
        counts,
        start=date_from.date(),
        end=date_to.date(),
    )
    if not series or sum(p["jobs"] for p in series) == 0:
        return []
    return series
