"""Shared helpers for evidence-coach briefs."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.analytics.country_filter import parse_country_codes
from app.analytics.evidence_gate import (
    DEFAULT_MIN_EVIDENCE,
    count_thin_in_query,
    evidence_meta,
    parse_min_evidence,
)
from app.analytics.job_query import base_job_query
from app.analytics.lenses import resolve_job_id_subquery
from app.core.config import get_settings
from app.storage.models import Technology, UserProfile, UserSkill

MIN_SAMPLE = 5
THIN_SAMPLE = 20
DEFAULT_LENS = "market"
EVIDENCE_LIMITS_NOTE = (
    "Thin-evidence jobs (capped/snapshot sources) excluded when min_evidence=standard."
)

BRIEF_TYPES: frozenset[str] = frozenset(
    {
        "rising_cooling",
        "where_demand",
        "adjacent",
        "focus_vs_market",
        "suggest_watches",
    }
)


def base_payload(
    *,
    brief_type: str,
    lens: str,
    sample_size: int,
    evidence: list[dict[str, Any]],
    narrative: str,
    limits: str,
    status: str,
    extra: Optional[dict[str, Any]] = None,
    min_evidence: Optional[str] = DEFAULT_MIN_EVIDENCE,
    excluded_thin_n: int = 0,
) -> dict[str, Any]:
    tier = parse_min_evidence(min_evidence)
    out: dict[str, Any] = {
        "brief_type": brief_type,
        "lens": lens,
        "sample_size": sample_size,
        "evidence": evidence,
        "narrative": narrative,
        "limits": limits,
        "methodology_version": get_settings().methodology_version,
        "status": status,
        **evidence_meta(min_evidence=tier, excluded_thin_n=excluded_thin_n),
    }
    if extra:
        out.update(extra)
    return out


def lens_sample_size(
    db: Session,
    *,
    lens: str,
    query_ids: Optional[Sequence[int]],
    days: int,
    country_code: Optional[str] = None,
    min_evidence: Optional[str] = DEFAULT_MIN_EVIDENCE,
) -> int:
    """Count canonical jobs for lens ∩ countries ∩ period ∩ min_evidence."""
    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=days) if days else None
    job_id_subq = resolve_job_id_subquery(db, lens, query_ids, days=days)
    tier = parse_min_evidence(min_evidence)
    q = base_job_query(
        date_from=date_from,
        date_to=now if days else None,
        country_code=country_code,
        job_id_subq=job_id_subq,
        min_evidence=tier,
    )
    return int(db.scalar(select(func.count()).select_from(q.subquery())) or 0)


def lens_excluded_thin_n(
    db: Session,
    *,
    lens: str,
    query_ids: Optional[Sequence[int]],
    days: int,
    country_code: Optional[str] = None,
    min_evidence: Optional[str] = DEFAULT_MIN_EVIDENCE,
) -> int:
    """How many thin jobs sit in the ungated corpus for this slice."""
    tier = parse_min_evidence(min_evidence)
    if tier != "standard":
        return 0
    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=days) if days else None
    job_id_subq = resolve_job_id_subquery(db, lens, query_ids, days=days)
    corpus_all = base_job_query(
        date_from=date_from,
        date_to=now if days else None,
        country_code=country_code,
        job_id_subq=job_id_subq,
        min_evidence=None,
    )
    return count_thin_in_query(db, corpus_all)


def with_evidence_limits(limits: str) -> str:
    if EVIDENCE_LIMITS_NOTE in limits:
        return limits
    return f"{limits} {EVIDENCE_LIMITS_NOTE}"


def status_for_n(n: int) -> str:
    if n < MIN_SAMPLE:
        return "refused"
    if n < THIN_SAMPLE:
        return "thin_sample"
    return "ok"


def flat_lens(lens: str) -> str:
    """Flat analytics reject ``compare`` payloads; use market side."""
    return "market" if lens == "compare" else lens


def geo_label(country_code: Optional[str]) -> str:
    codes = parse_country_codes(country_code)
    return f" countries={','.join(codes)}" if codes else ""


def countries_extra(country_code: Optional[str]) -> dict[str, Any]:
    codes = parse_country_codes(country_code)
    return {"countries": codes or None}


def profile_skill_names(db: Session) -> set[str]:
    profile = db.scalar(select(UserProfile).order_by(UserProfile.id).limit(1))
    if not profile:
        return set()
    return set(
        db.scalars(
            select(Technology.canonical_name)
            .join(UserSkill, UserSkill.technology_id == Technology.id)
            .where(UserSkill.profile_id == profile.id)
        ).all()
    )


def thin_or_refuse(
    *,
    brief_type: str,
    lens: str,
    sample_size: int,
    limits: str,
    excluded_thin_n: int = 0,
    extra: Optional[dict[str, Any]] = None,
) -> Optional[dict[str, Any]]:
    if status_for_n(sample_size) != "refused":
        return None
    payload = base_payload(
        brief_type=brief_type,
        lens=lens,
        sample_size=sample_size,
        evidence=[],
        narrative=(
            f"Refused: sample too thin (n={sample_size}, need ≥{MIN_SAMPLE}). "
            "Sync discovery/focus crawlers and retry."
        ),
        limits=with_evidence_limits(limits),
        status="refused",
        excluded_thin_n=excluded_thin_n,
        extra=extra,
    )
    if brief_type == "suggest_watches":
        payload["proposed_intents"] = []
    return payload
