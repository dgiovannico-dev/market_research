from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.analytics.country_filter import parse_country_codes
from app.analytics.coverage_notes import attach_coverage_notes, coverage_notes_for_slice
from app.analytics.job_query import CLOSED_JOB_STATUSES
from app.analytics.lenses import apply_lens_filter, compare_counts, parse_lens
from app.storage.models import Job, JobRate, JobSkill, Technology

FOCUS_COUNTRIES = [
    "IT",
    "CH",
    "DE",
    "AT",
    "FR",
    "NL",
    "BE",
    "LU",
    "IE",
    "ES",
    "GB",
    "US",
    "WW",
    "unknown",
]


def _map_series(
    db: Session,
    *,
    open_jobs,
    codes: Optional[list[str]],
    days: int,
    lens_name: str,
    query_ids: Optional[Sequence[int]],
) -> dict[str, Any]:
    """All ISO country counts for choropleth (excludes unknown from map_items)."""
    rows = db.execute(
        apply_lens_filter(
            select(Job.country_code, func.count())
            .where(*open_jobs)
            .group_by(Job.country_code)
            .order_by(func.count().desc())
            .limit(250),
            db,
            lens=lens_name,
            query_ids=query_ids,
        )
    ).all()
    if codes:
        code_set = set(codes)
        rows = [(c, n) for c, n in rows if c in code_set]
    map_items = [
        {"country_code": (c or "unknown"), "jobs": int(n)}
        for c, n in rows
        if c and c != "unknown" and n
    ]
    unknown_n = sum(int(n) for c, n in rows if not c or c == "unknown")
    return {
        "period_days": days,
        "lens": lens_name,
        "query_ids": list(query_ids) if query_ids else None,
        "countries": codes or None,
        "for_map": True,
        "map_items": map_items,
        "unknown_jobs": unknown_n,
        "disclaimer": "Observed jobs by country_code in this DB; not full market census.",
        "items": [],
    }


def country_comparison(
    db: Session,
    *,
    days: int = 90,
    country_code: Optional[str] = None,
    lens: str = "market",
    query_ids: Optional[Sequence[int]] = None,
    for_map: bool = False,
) -> dict[str, Any]:
    lens_name = parse_lens(lens)
    codes = parse_country_codes(country_code)
    if lens_name == "compare":
        market = country_comparison(
            db,
            days=days,
            country_code=country_code,
            lens="market",
            query_ids=query_ids,
            for_map=for_map,
        )
        focus = country_comparison(
            db,
            days=days,
            country_code=country_code,
            lens="focus",
            query_ids=query_ids,
            for_map=for_map,
        )
        # Lift shared metadata so clients need not special-case compare nesting.
        return {
            "lens": "compare",
            "query_ids": list(query_ids) if query_ids else None,
            "countries": codes or None,
            **compare_counts(
                db, query_ids=query_ids, days=days, country_code=country_code
            ),
            "period_days": market.get("period_days", days),
            "disclaimer": market.get("disclaimer"),
            "coverage_notes": market.get("coverage_notes") or [],
            "market": market,
            "focus": focus,
        }

    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=days)
    # Match DSS corpus: exclude closed / closed_stale / removed_from_source.
    open_jobs = (
        Job.is_canonical.is_(True),
        Job.published_at >= date_from,
        Job.status.notin_(CLOSED_JOB_STATUSES),
    )
    if for_map:
        out = _map_series(
            db,
            open_jobs=open_jobs,
            codes=codes,
            days=days,
            lens_name=lens_name,
            query_ids=query_ids,
        )
        notes = coverage_notes_for_slice(
            db, country_code=country_code, date_from=date_from
        )
        return attach_coverage_notes(out, notes)

    base = apply_lens_filter(
        select(Job).where(*open_jobs),
        db,
        lens=lens_name,
        query_ids=query_ids,
    )

    scope = codes if codes else FOCUS_COUNTRIES
    items = []
    for code in scope:
        q = base.where(Job.country_code == code)
        total = db.scalar(select(func.count()).select_from(q.subquery())) or 0
        if total == 0:
            continue
        remote = (
            db.scalar(
                select(func.count()).select_from(q.where(Job.remote_type == "remote").subquery())
            )
            or 0
        )
        b2b = (
            db.scalar(
                select(func.count()).select_from(
                    q.where(Job.contract_type.in_(["freelance", "b2b", "contractor"])).subquery()
                )
            )
            or 0
        )
        allowed = (
            db.scalar(
                select(func.count()).select_from(
                    q.where(Job.residence_restriction == "explicitly_allowed").subquery()
                )
            )
            or 0
        )
        restricted = (
            db.scalar(
                select(func.count()).select_from(
                    q.where(Job.residence_restriction == "explicitly_restricted").subquery()
                )
            )
            or 0
        )
        with_rate = (
            db.scalar(
                apply_lens_filter(
                    select(func.count(func.distinct(JobRate.job_id)))
                    .select_from(JobRate)
                    .join(Job)
                    .where(
                        *open_jobs,
                        Job.country_code == code,
                    ),
                    db,
                    lens=lens_name,
                    query_ids=query_ids,
                )
            )
            or 0
        )
        top_tech = db.execute(
            apply_lens_filter(
                select(Technology.canonical_name, func.count(JobSkill.id))
                .join(JobSkill)
                .join(Job)
                .where(
                    *open_jobs,
                    Job.country_code == code,
                )
                .group_by(Technology.canonical_name)
                .order_by(func.count(JobSkill.id).desc())
                .limit(5),
                db,
                lens=lens_name,
                query_ids=query_ids,
            )
        ).all()
        items.append(
            {
                "country_code": code,
                "jobs_observed": total,
                "remote_share": round(remote / total, 4),
                "b2b_freelance_share": round(b2b / total, 4),
                "explicitly_allowed_residence": allowed,
                "explicitly_restricted_residence": restricted,
                "unclear_residence": total - allowed - restricted,
                "jobs_with_rate": with_rate,
                "top_technologies": [{"name": n, "mentions": c} for n, c in top_tech],
                "evidence_kind": "derived",
                "legal_disclaimer": (
                    "Not legal/tax advice. Residence access categories are text-extracted; "
                    "remote != acceptance of Italian residents."
                ),
            }
        )

    out = {
        "period_days": days,
        "lens": lens_name,
        "query_ids": list(query_ids) if query_ids else None,
        "countries": codes or None,
        "disclaimer": "Observed jobs by country_code in this DB; not full market census.",
        "items": items,
    }
    notes = coverage_notes_for_slice(
        db, country_code=country_code, date_from=date_from
    )
    return attach_coverage_notes(out, notes)
