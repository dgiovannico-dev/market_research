"""Temporal series for top technologies / countries (Relations dashboard)."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Any, Literal, Optional, Sequence

from sqlalchemy import Date, cast, func, select
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
from app.storage.models import Job, JobSkill, Technology

Grain = Literal["day", "week", "month"]

_SERIES_LIMITS = (
    "Observed inventory only; not a census. Counts are distinct jobs in each bucket."
)


def choose_grain(days: int, grain: Optional[str] = None) -> Grain:
    """Pick day/week/month from optional override or window length."""
    if grain:
        cleaned = str(grain).strip().lower()
        if cleaned in ("day", "week", "month"):
            return cleaned  # type: ignore[return-value]
        raise ValueError(f"invalid grain={grain!r}; use day|week|month")
    if days <= 30:
        return "day"
    if days <= 180:
        return "week"
    return "month"


def bucket_label_for_date(d: date, grain: Grain) -> str:
    """UTC calendar date → bucket key for the given grain."""
    if grain == "day":
        return d.isoformat()
    if grain == "week":
        iso = d.isocalendar()
        return f"{iso.year}-W{iso.week:02d}"
    return f"{d.year:04d}-{d.month:02d}"


def iter_bucket_labels(start: date, end: date, grain: Grain) -> list[str]:
    """Continuous bucket axis from start..end inclusive (UTC dates)."""
    if start > end:
        return []
    labels: list[str] = []
    seen: set[str] = set()
    if grain == "day":
        cursor = start
        while cursor <= end:
            labels.append(cursor.isoformat())
            cursor += timedelta(days=1)
        return labels
    if grain == "week":
        # Align to ISO week Monday of start, then step by 7 days.
        cursor = start - timedelta(days=start.weekday())
        while cursor <= end:
            label = bucket_label_for_date(cursor, "week")
            if label not in seen:
                seen.add(label)
                labels.append(label)
            cursor += timedelta(days=7)
        # Ensure end's week is included even if start alignment skipped it.
        end_label = bucket_label_for_date(end, "week")
        if end_label not in seen:
            labels.append(end_label)
        return labels
    # month
    y, m = start.year, start.month
    ey, em = end.year, end.month
    while (y, m) <= (ey, em):
        labels.append(f"{y:04d}-{m:02d}")
        if m == 12:
            y, m = y + 1, 1
        else:
            m += 1
    return labels


def fill_bucket_counts(
    counts: dict[str, int],
    buckets: Sequence[str],
) -> list[dict[str, Any]]:
    """Fill missing buckets with 0 for a continuous axis."""
    return [{"bucket": b, "count": int(counts.get(b, 0))} for b in buckets]


def corpus_setup(
    db: Session,
    *,
    days: int,
    country_code: Optional[str],
    lens: Optional[str],
    query_ids: Optional[Sequence[int]],
    min_evidence: Optional[str],
) -> tuple[Any, int, int, Optional[str], datetime, datetime]:
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
    sample_size = int(db.scalar(select(func.count()).select_from(job_id_sub)) or 0)
    return select(job_id_sub.c.id), sample_size, excluded_thin_n, tier, date_from, now


def _empty_series(
    *,
    days: int,
    grain: Grain,
    excluded_thin_n: int,
    tier: Optional[str],
) -> dict[str, Any]:
    return {
        "period_days": days,
        "grain": grain,
        "sample_size": 0,
        "series": [],
        **evidence_meta(min_evidence=tier, excluded_thin_n=excluded_thin_n),
        "limits": _SERIES_LIMITS,
    }


def _roll_day_rows(
    rows: Sequence[tuple[Any, Any, Any]],
    *,
    grain: Grain,
    top: int,
    date_from: datetime,
    date_to: datetime,
) -> list[dict[str, Any]]:
    """rows: (key, day_date, count) → top-N series with filled buckets."""
    key_day: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    key_total: dict[str, int] = defaultdict(int)
    for key, day_val, cnt in rows:
        if not key:
            continue
        if isinstance(day_val, datetime):
            d = day_val.date()
        elif isinstance(day_val, date):
            d = day_val
        else:
            continue
        label = bucket_label_for_date(d, grain)
        n = int(cnt)
        key_day[str(key)][label] += n
        key_total[str(key)] += n

    top_keys = [
        k
        for k, _ in sorted(key_total.items(), key=lambda x: (-x[1], x[0]))[: max(1, top)]
    ]
    buckets = iter_bucket_labels(date_from.date(), date_to.date(), grain)
    return [
        {"key": key, "points": fill_bucket_counts(key_day[key], buckets)}
        for key in top_keys
    ]


def technology_series(
    db: Session,
    *,
    days: int = 90,
    country_code: Optional[str] = None,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    min_evidence: Optional[str] = DEFAULT_MIN_EVIDENCE,
    top: int = 8,
    grain: Optional[str] = None,
) -> dict[str, Any]:
    resolved = choose_grain(days, grain)
    job_ids, sample_size, excluded_thin_n, tier, date_from, now = corpus_setup(
        db,
        days=days,
        country_code=country_code,
        lens=lens,
        query_ids=query_ids,
        min_evidence=min_evidence,
    )
    if sample_size == 0:
        return _empty_series(
            days=days, grain=resolved, excluded_thin_n=excluded_thin_n, tier=tier
        )

    day_expr = cast(Job.published_at, Date)
    rows = db.execute(
        select(
            Technology.canonical_name,
            day_expr,
            func.count(func.distinct(JobSkill.job_id)),
        )
        .select_from(JobSkill)
        .join(Technology, Technology.id == JobSkill.technology_id)
        .join(Job, Job.id == JobSkill.job_id)
        .where(
            JobSkill.job_id.in_(job_ids),
            Job.published_at.is_not(None),
        )
        .group_by(Technology.canonical_name, day_expr)
    ).all()

    series = _roll_day_rows(
        rows, grain=resolved, top=top, date_from=date_from, date_to=now
    )
    return {
        "period_days": days,
        "grain": resolved,
        "sample_size": sample_size,
        "series": series,
        **evidence_meta(min_evidence=tier, excluded_thin_n=excluded_thin_n),
        "limits": _SERIES_LIMITS,
    }


def country_series(
    db: Session,
    *,
    days: int = 90,
    country_code: Optional[str] = None,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    min_evidence: Optional[str] = DEFAULT_MIN_EVIDENCE,
    top: int = 8,
    grain: Optional[str] = None,
) -> dict[str, Any]:
    resolved = choose_grain(days, grain)
    job_ids, sample_size, excluded_thin_n, tier, date_from, now = corpus_setup(
        db,
        days=days,
        country_code=country_code,
        lens=lens,
        query_ids=query_ids,
        min_evidence=min_evidence,
    )
    if sample_size == 0:
        return _empty_series(
            days=days, grain=resolved, excluded_thin_n=excluded_thin_n, tier=tier
        )

    day_expr = cast(Job.published_at, Date)
    rows = db.execute(
        select(
            Job.country_code,
            day_expr,
            func.count(func.distinct(Job.id)),
        )
        .where(
            Job.id.in_(job_ids),
            Job.published_at.is_not(None),
            Job.country_code.is_not(None),
            Job.country_code != "unknown",
        )
        .group_by(Job.country_code, day_expr)
    ).all()

    series = _roll_day_rows(
        rows, grain=resolved, top=top, date_from=date_from, date_to=now
    )
    return {
        "period_days": days,
        "grain": resolved,
        "sample_size": sample_size,
        "series": series,
        **evidence_meta(min_evidence=tier, excluded_thin_n=excluded_thin_n),
        "limits": _SERIES_LIMITS,
    }
