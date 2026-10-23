"""Analytics lenses over job_intent_matches (SPEC-research-intents §3.3).

API / KPI defaults (Task 5):

- ``lens=None`` / omit / ``all``: no filter — all canonical jobs (backward
  compatible). Product UI should pass ``lens=market`` explicitly.
- ``lens="market"``: unlabeled (no matches) **or** matched to ≥1 discovery.
  Focus-only jobs are excluded.
- ``lens="focus"``: matched to focus ``query_ids`` (default: all enabled focus).
- ``lens="compare"``: both sets + ``market_n`` / ``focus_n`` / ``overlap_n``.

``job_ids_for_lens(...)`` defaults to ``market`` when called directly in tests.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Literal, Optional, Sequence, Union

from sqlalchemy import Select, exists, func, or_, select
from sqlalchemy.orm import Session

from app.analytics.country_filter import country_codes_clause, parse_country_codes
from app.storage.models import Job, JobIntentMatch, SearchQuery

LensName = Literal["market", "focus", "compare"]
LensJobIds = Union[set[int], dict[str, set[int]]]


def normalize_lens(lens: Optional[str] = None) -> Optional[LensName]:
    """Map param to a lens name, or ``None`` for unfiltered (``all`` / omit)."""
    if lens is None:
        return None
    name = str(lens).strip().lower()
    if name in ("", "all"):
        return None
    if name not in ("market", "focus", "compare"):
        raise ValueError(f"Unknown lens: {lens!r}; expected market|focus|compare|all")
    return name  # type: ignore[return-value]


# API/KPI alias — does **not** coerce None to market (backward-compatible all-jobs).
parse_lens = normalize_lens


def parse_query_ids(
    raw: Optional[Union[str, Sequence[Union[str, int]]]] = None,
) -> Optional[list[int]]:
    """Parse ``query_ids`` from comma-separated string and/or repeated params."""
    if raw is None:
        return None
    parts: list[str] = []
    if isinstance(raw, str):
        parts = raw.split(",")
    else:
        for item in raw:
            parts.extend(str(item).split(","))
    out: list[int] = []
    for piece in parts:
        piece = piece.strip()
        if not piece:
            continue
        out.append(int(piece))
    return out or None


def _published_since(days: Optional[int]) -> Optional[datetime]:
    if days is None:
        return None
    return datetime.now(timezone.utc) - timedelta(days=days)


def _with_days(q: Select, days: Optional[int]) -> Select:
    since = _published_since(days)
    if since is not None:
        q = q.where(Job.published_at >= since)
    return q


def _any_match_exists():
    return exists(
        select(1).select_from(JobIntentMatch).where(JobIntentMatch.job_id == Job.id)
    )


def _discovery_match_exists():
    return exists(
        select(1)
        .select_from(JobIntentMatch)
        .join(SearchQuery, SearchQuery.id == JobIntentMatch.query_id)
        .where(
            JobIntentMatch.job_id == Job.id,
            SearchQuery.kind == "discovery",
            SearchQuery.deleted_at.is_(None),
        )
    )


def _focus_match_exists(query_ids: Optional[Sequence[int]] = None):
    cond = [
        JobIntentMatch.job_id == Job.id,
        SearchQuery.kind == "focus",
        SearchQuery.deleted_at.is_(None),
    ]
    if query_ids:
        cond.append(JobIntentMatch.query_id.in_(list(query_ids)))
    else:
        cond.append(SearchQuery.enabled.is_(True))
    return exists(
        select(1)
        .select_from(JobIntentMatch)
        .join(SearchQuery, SearchQuery.id == JobIntentMatch.query_id)
        .where(*cond)
    )


def market_job_id_subquery(*, days: Optional[int] = None) -> Select:
    return _with_days(
        select(Job.id).where(
            Job.is_canonical.is_(True),
            or_(~_any_match_exists(), _discovery_match_exists()),
        ),
        days,
    )


def focus_job_id_subquery(
    query_ids: Optional[Sequence[int]] = None, *, days: Optional[int] = None
) -> Select:
    return _with_days(
        select(Job.id).where(
            Job.is_canonical.is_(True),
            _focus_match_exists(query_ids),
        ),
        days,
    )


def resolve_job_id_subquery(
    db: Session,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    *,
    days: Optional[int] = None,
) -> Optional[Select]:
    """Job-id selectable for a lens, or ``None`` when unfiltered."""
    del db
    name = normalize_lens(lens)
    if name is None:
        return None
    if name == "market":
        return market_job_id_subquery(days=days)
    if name == "focus":
        return focus_job_id_subquery(query_ids, days=days)
    return select(Job.id).where(
        Job.is_canonical.is_(True),
        or_(
            Job.id.in_(market_job_id_subquery(days=days)),
            Job.id.in_(focus_job_id_subquery(query_ids, days=days)),
        ),
    )


def apply_lens_filter(
    stmt: Select,
    db: Session,
    *,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    days: Optional[int] = None,
) -> Select:
    """Restrict a Job-based select; no-op when lens is None/all."""
    subq = resolve_job_id_subquery(db, lens, query_ids, days=days)
    if subq is None:
        return stmt
    return stmt.where(Job.id.in_(subq))


def _country_filter(stmt: Select, country_code: Optional[str] = None) -> Select:
    codes = parse_country_codes(country_code)
    clause = country_codes_clause(codes)
    if clause is not None:
        return stmt.where(clause)
    return stmt


def compare_counts(
    db: Session,
    *,
    query_ids: Optional[Sequence[int]] = None,
    days: Optional[int] = None,
    country_code: Optional[str] = None,
) -> dict[str, int]:
    """Lens set sizes; optional country/days align badges with nested KPI filters."""
    market_subq = _country_filter(market_job_id_subquery(days=days), country_code)
    focus_subq = _country_filter(focus_job_id_subquery(query_ids, days=days), country_code)
    market_n = db.scalar(select(func.count()).select_from(market_subq.subquery())) or 0
    focus_n = db.scalar(select(func.count()).select_from(focus_subq.subquery())) or 0
    overlap_n = (
        db.scalar(
            select(func.count()).select_from(
                select(Job.id)
                .where(Job.id.in_(market_subq), Job.id.in_(focus_subq))
                .subquery()
            )
        )
        or 0
    )
    return {"market_n": int(market_n), "focus_n": int(focus_n), "overlap_n": int(overlap_n)}


def job_ids_for_lens(
    db: Session,
    *,
    lens: LensName = "market",
    query_ids: Optional[Sequence[int]] = None,
    days: Optional[int] = None,
) -> LensJobIds:
    """Materialize canonical job ids for ``market`` / ``focus`` / ``compare``."""
    if lens == "market":
        return set(db.scalars(market_job_id_subquery(days=days)).all())
    if lens == "focus":
        return set(db.scalars(focus_job_id_subquery(query_ids, days=days)).all())
    if lens == "compare":
        return {
            "market": set(db.scalars(market_job_id_subquery(days=days)).all()),
            "focus": set(db.scalars(focus_job_id_subquery(query_ids, days=days)).all()),
        }
    raise ValueError(f"Unknown lens: {lens!r}")


def compare_payload(
    db: Session,
    *,
    query_ids: Optional[Sequence[int]] = None,
    days: Optional[int] = None,
) -> dict[str, Any]:
    paired = job_ids_for_lens(db, lens="compare", query_ids=query_ids, days=days)
    assert isinstance(paired, dict)
    return {
        "lens": "compare",
        "query_ids": list(query_ids) if query_ids else None,
        **compare_counts(db, query_ids=query_ids, days=days),
        "market_ids": paired["market"],
        "focus_ids": paired["focus"],
    }


def resolve_lens_job_ids(
    db: Session,
    *,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    days: Optional[int] = None,
) -> Optional[set[int]]:
    """Materialized id set for a lens, or ``None`` when unfiltered."""
    name = normalize_lens(lens)
    if name is None:
        return None
    if name == "compare":
        paired = job_ids_for_lens(db, lens="compare", query_ids=query_ids, days=days)
        assert isinstance(paired, dict)
        return set(paired["market"]) | set(paired["focus"])
    ids = job_ids_for_lens(db, lens=name, query_ids=query_ids, days=days)
    assert isinstance(ids, set)
    return ids
