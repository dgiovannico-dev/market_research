"""Job skill/rate sync — skip clear+reinsert when identity unchanged."""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Optional

from sqlalchemy.orm import Session

from app.storage.models import Job, JobRate, JobSkill, Technology

# Identity used to decide whether skills need a rewrite.
SkillIdentity = tuple[int, str, str]  # technology_id, importance, evidence_kind
# Identity for a single advertised rate skip path.
RateIdentity = tuple[Optional[float], Optional[float], Optional[str], str]


def skill_identities(skills: Iterable[Any]) -> frozenset[SkillIdentity]:
    return frozenset(
        (int(s.technology_id), str(s.importance), str(s.evidence_kind)) for s in skills
    )


def desired_skill_rows(
    classified_techs: Iterable[Mapping[str, Any]],
    tech_map: Mapping[str, Technology],
) -> list[dict[str, Any]]:
    """Resolve classified tech dicts to insertable JobSkill field dicts."""
    rows: list[dict[str, Any]] = []
    for tech in classified_techs:
        technology = tech_map.get(tech["canonical_name"])
        if not technology:
            continue
        rows.append(
            {
                "technology_id": technology.id,
                "importance": tech["importance"],
                "extraction_method": tech["extraction_method"],
                "evidence_kind": tech["evidence_kind"],
                "confidence": tech["confidence"],
                "evidence_span": tech.get("evidence_span"),
            }
        )
    return rows


def desired_skill_identities(rows: Iterable[Mapping[str, Any]]) -> frozenset[SkillIdentity]:
    return frozenset(
        (int(r["technology_id"]), str(r["importance"]), str(r["evidence_kind"])) for r in rows
    )


def rate_identity_from_row(rate: Any) -> RateIdentity:
    return (
        rate.amount_min,
        rate.amount_max,
        rate.currency,
        str(rate.unit or "unknown"),
    )


def rate_identity_from_classified(rate: Mapping[str, Any]) -> RateIdentity:
    return (
        rate.get("amount_min"),
        rate.get("amount_max"),
        rate.get("currency"),
        str(rate.get("unit") or "unknown"),
    )


def sync_job_skills(
    db: Session,
    job: Job,
    *,
    classified_techs: Iterable[Mapping[str, Any]],
    tech_map: Mapping[str, Technology],
) -> bool:
    """Replace job.skills only when identity set changed. Returns True if wrote."""
    rows = desired_skill_rows(classified_techs, tech_map)
    if skill_identities(job.skills) == desired_skill_identities(rows):
        return False
    job.skills.clear()
    db.flush()
    for row in rows:
        job.skills.append(JobSkill(**row))
    return True


def sync_job_rates(
    db: Session,
    job: Job,
    *,
    classified_rate: Optional[Mapping[str, Any]],
) -> bool:
    """Replace rates only when the single advertised rate identity changed.

    Returns True if wrote. No-op when both sides empty, or when exactly one
    existing advertised rate matches amount/currency/unit of the new rate.
    """
    existing = list(job.rates)
    if classified_rate is None:
        if not existing:
            return False
        job.rates.clear()
        db.flush()
        return True

    desired = rate_identity_from_classified(classified_rate)
    if (
        len(existing) == 1
        and getattr(existing[0], "rate_type", "advertised") == "advertised"
        and rate_identity_from_row(existing[0]) == desired
    ):
        return False

    job.rates.clear()
    db.flush()
    job.rates.append(
        JobRate(
            amount_min=classified_rate.get("amount_min"),
            amount_max=classified_rate.get("amount_max"),
            currency=classified_rate.get("currency"),
            unit=classified_rate.get("unit", "unknown"),
            rate_type=classified_rate.get("rate_type", "advertised"),
            evidence_text=classified_rate.get("evidence_text"),
            extraction_method=classified_rate.get("extraction_method", "rules"),
            evidence_kind=classified_rate.get("evidence_kind", "extracted"),
            confidence=classified_rate.get("confidence"),
        )
    )
    return True
