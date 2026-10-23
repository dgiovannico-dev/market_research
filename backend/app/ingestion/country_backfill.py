"""Re-resolve Job.country_code for rows still marked unknown."""

from __future__ import annotations

from collections import Counter
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.classification.rules import _detect_country  # private heuristic; domain facade is public classify_job
from app.ingestion.geo_defaults import SOURCE_DEFAULT_COUNTRY
from app.storage.enums import CLOSED_JOB_STATUSES
from app.storage.models import Job, Source


def resolve_country_code(
    *,
    title: str = "",
    description: str | None,
    location: str | None,
    connector_type: str | None,
) -> str:
    """Prefer text heuristics; fall back to the connector's home market.

    Uses ``_detect_country`` only (not full ``classify_job``) so backfill stays
    fast on multi-thousand corpora. ``title`` is accepted for call-site
    symmetry with classify but unused today.
    """
    _ = title
    detected = _detect_country(location, description)
    if detected and detected != "unknown":
        return detected
    if connector_type:
        stamp = SOURCE_DEFAULT_COUNTRY.get(connector_type)
        if stamp:
            return stamp
    return "unknown"


def backfill_country_codes(
    db: Session,
    *,
    only_unknown: bool = True,
    limit: int | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Update country_code from location text + national-board defaults.

    By default only rows with ``country_code == 'unknown'`` are touched.
    """
    stmt = (
        select(Job, Source.connector_type)
        .join(Source, Source.id == Job.source_id)
        .where(
            Job.is_canonical.is_(True),
            Job.status.notin_(CLOSED_JOB_STATUSES),
        )
        .order_by(Job.id)
    )
    if only_unknown:
        stmt = stmt.where(Job.country_code == "unknown")
    if limit is not None:
        stmt = stmt.limit(limit)

    rows = db.execute(stmt).all()
    updated = 0
    skipped = 0
    still_unknown = 0
    by_code: Counter[str] = Counter()
    by_source: Counter[str] = Counter()

    for job, connector_type in rows:
        new_code = resolve_country_code(
            title=job.title_original or "",
            description=job.description_original,
            location=job.location_original,
            connector_type=connector_type,
        )
        if new_code == "unknown":
            still_unknown += 1
            skipped += 1
            continue
        if job.country_code == new_code:
            skipped += 1
            continue
        by_code[new_code] += 1
        by_source[str(connector_type or "?")] += 1
        updated += 1
        if not dry_run:
            job.country_code = new_code

    return {
        "scanned": len(rows),
        "updated": updated,
        "skipped": skipped,
        "still_unknown": still_unknown,
        "dry_run": dry_run,
        "only_unknown": only_unknown,
        "by_code": dict(by_code.most_common()),
        "by_source": dict(by_source.most_common(25)),
    }
