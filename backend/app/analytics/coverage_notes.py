"""Footnotes when a geo slice is capped / snapshot / thin-heavy."""

from __future__ import annotations

from typing import Any, Optional, Sequence, Union

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.analytics.job_query import base_job_query
from app.storage.enums import EvidenceTier
from app.storage.models import Job, Source

CoverageNote = dict[str, Any]
CoverageNoteLike = Union[str, CoverageNote]

# Connectors known to ship capped samples or open-data snapshots.
_CAPPED_OR_SNAPSHOT = frozenset(
    {
        "viewjobs",
        "jobbank_ca",
        "devglobaljobs",
        "okemprego",
    }
)


def coverage_notes_for_slice(
    db: Session,
    *,
    country_code: Optional[str] = None,
    job_id_subq=None,
    date_from=None,
) -> list[CoverageNote]:
    """Return structured footnotes for DSS summary / countries responses.

    Each note has ``code`` (for i18n) plus an English ``message`` fallback.
    """
    notes: list[CoverageNote] = []
    corpus = base_job_query(
        date_from=date_from,
        country_code=country_code,
        job_id_subq=job_id_subq,
        min_evidence=None,
    )
    total = int(db.scalar(select(func.count()).select_from(corpus.subquery())) or 0)
    if total == 0:
        return notes

    thin_n = int(
        db.scalar(
            select(func.count()).select_from(
                corpus.where(Job.evidence_tier == EvidenceTier.thin.value).subquery()
            )
        )
        or 0
    )
    if thin_n:
        pct = round((thin_n / total) * 100.0, 1)
        message = (
            f"{thin_n} jobs ({pct}%) are thin evidence (title/snippet/synthetic) "
            "and are excluded from skills/rates/briefs when min_evidence=standard."
        )
        notes.append(
            {
                "code": "thin_evidence",
                "thin_n": thin_n,
                "pct": pct,
                "message": message,
            }
        )

    source_ids = [
        sid
        for (sid,) in db.execute(
            select(Job.source_id).where(Job.id.in_(corpus.with_only_columns(Job.id))).distinct()
        ).all()
    ]
    if not source_ids:
        return notes
    connectors = {
        s.connector_type
        for s in db.scalars(select(Source).where(Source.id.in_(source_ids))).all()
        if s.connector_type
    }
    hit = sorted(connectors & _CAPPED_OR_SNAPSHOT)
    if hit:
        sources = ", ".join(hit)
        message = (
            f"Slice includes capped or snapshot sources ({sources}) "
            "— counts are not a census of the national market."
        )
        notes.append(
            {
                "code": "capped_sources",
                "sources": sources,
                "message": message,
            }
        )
    return notes


def attach_coverage_notes(
    payload: dict[str, Any], notes: Sequence[CoverageNoteLike]
) -> dict[str, Any]:
    if notes:
        payload["coverage_notes"] = list(notes)
    return payload
