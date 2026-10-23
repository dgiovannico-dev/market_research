"""Parse and apply DSS min_evidence corpus gates."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import ColumnElement, Select, func, select
from sqlalchemy.orm import Session

from app.storage.enums import EvidenceTier
from app.storage.models import Job

DEFAULT_MIN_EVIDENCE = EvidenceTier.standard.value


def parse_min_evidence(value: Optional[str] = None) -> Optional[str]:
    """Return ``standard`` (filter), ``None`` (no filter / all), or raise.

    Default for skills/rates/briefs callers: pass ``DEFAULT_MIN_EVIDENCE``.
    Explicit ``all`` / empty disables the gate (Quality / inventory).
    """
    if value is None:
        return DEFAULT_MIN_EVIDENCE
    cleaned = str(value).strip().lower()
    if cleaned in ("", "all", "any"):
        return None
    if cleaned == EvidenceTier.standard.value:
        return EvidenceTier.standard.value
    if cleaned == EvidenceTier.thin.value:
        # Allow querying thin-only for diagnostics; not the DSS default.
        return EvidenceTier.thin.value
    raise ValueError(
        f"invalid min_evidence={value!r}; use standard|all|thin"
    )


def evidence_tier_clause(min_evidence: Optional[str]) -> ColumnElement[bool] | None:
    if min_evidence in (
        EvidenceTier.standard.value,
        EvidenceTier.thin.value,
    ):
        return Job.evidence_tier == min_evidence
    return None


def count_thin_in_query(db: Session, job_select: Select) -> int:
    """How many jobs in the (already status-filtered) select are thin."""
    sub = job_select.with_only_columns(Job.id).subquery()
    return int(
        db.scalar(
            select(func.count())
            .select_from(Job)
            .where(Job.id.in_(select(sub.c.id)), Job.evidence_tier == EvidenceTier.thin.value)
        )
        or 0
    )


def evidence_meta(
    *,
    min_evidence: Optional[str],
    excluded_thin_n: int,
) -> dict[str, Any]:
    return {
        "min_evidence": min_evidence or "all",
        "excluded_thin_n": excluded_thin_n,
    }
