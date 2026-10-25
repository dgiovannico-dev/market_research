"""Study Advisor evidence pack + deterministic stub plans (SPEC-study-advisor)."""

from __future__ import annotations

import json
from typing import Any, Literal, Optional, Sequence

from pydantic import BaseModel, Field, ValidationError, field_validator
from sqlalchemy.orm import Session

from app.adapters.driven.llm.provider import get_llm_provider
from app.analytics.learning_candidates import learning_candidates
from app.analytics.study_llm_payload import (
    coerce_llm_plan_payload,
    compact_evidence_for_llm,
)
from app.analytics.study_schedule import build_weekly_schedule, normalize_busy_slots
from app.application.llm.prompts import resolve_prompt
from app.application.llm.runtime_config import resolve_llm_settings
from app.core.config import get_settings

# Re-export for tests / callers that import from study_advice
__all__ = [
    "StudyMilestone",
    "StudyPlan",
    "build_evidence_pack",
    "coerce_llm_plan_payload",
    "compact_evidence_for_llm",
    "generate_study_plan",
    "refine_study_plan",
    "stub_study_plan",
    "validate_plan_against_evidence",
]

Modality = Literal["employed_part_time", "freelance_full_time", "intensive"]

_WEEKLY_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "employed_part_time": [
        {"weekday": "tue", "start": "19:00", "end": "21:00", "label": "evening_block"},
        {"weekday": "thu", "start": "19:00", "end": "21:00", "label": "evening_block"},
        {"weekday": "sat", "start": "10:00", "end": "13:00", "label": "weekend_block"},
    ],
    "freelance_full_time": [
        {"weekday": "mon", "start": "09:00", "end": "12:00", "label": "morning_block"},
        {"weekday": "wed", "start": "09:00", "end": "12:00", "label": "morning_block"},
        {"weekday": "fri", "start": "14:00", "end": "17:00", "label": "afternoon_block"},
    ],
    "intensive": [
        {"weekday": d, "start": "09:00", "end": "13:00", "label": "daily_block"}
        for d in ("mon", "tue", "wed", "thu", "fri")
    ],
}


class StudyMilestone(BaseModel):
    week: int = Field(ge=1)
    title: str
    skills: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    hours: Optional[float] = None


class StudyPlan(BaseModel):
    title: str
    horizon_weeks: int = Field(ge=1, le=52)
    modality: Modality
    hours_per_week: float = Field(gt=0, le=80)
    stack_target: list[str] = Field(default_factory=list)
    milestones: list[StudyMilestone] = Field(default_factory=list)
    weekly_template: list[dict[str, Any]] = Field(default_factory=list)
    limits: list[str] = Field(default_factory=list)
    source: str = "stub"

    @field_validator("stack_target", "milestones", mode="before")
    @classmethod
    def _not_none(cls, v: Any) -> Any:
        return v if v is not None else []


def _attach_calendar(plan: StudyPlan, evidence: dict[str, Any]) -> StudyPlan:
    """Always rebuild weekly_template from hours + busy slots (ignore LLM noise)."""
    schedule = build_weekly_schedule(
        hours_per_week=float(evidence.get("hours_per_week") or plan.hours_per_week),
        modality=evidence.get("modality") or plan.modality,
        busy_slots=evidence.get("busy_slots"),
    )
    limits = list(plan.limits or [])
    for note in schedule.get("notes") or []:
        if note not in limits:
            limits.append(note)
    return plan.model_copy(
        update={
            "weekly_template": list(schedule.get("weekly_template") or []),
            "limits": limits,
        }
    )


def build_evidence_pack(
    db: Session,
    *,
    skills: list[str],
    certifications: Optional[list[str]] = None,
    hours_per_week: float = 6,
    modality: Modality = "employed_part_time",
    horizon_weeks: int = 8,
    days: int = 90,
    country_code: Optional[str] = None,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    min_evidence: Optional[str] = None,
    busy_slots: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    owned = [s.strip() for s in skills if s and str(s).strip()]
    compass = learning_candidates(
        db,
        owned_skills=owned,
        owned_certifications=certifications,
        days=days,
        country_code=country_code,
        lens=lens,
        query_ids=query_ids,
        min_evidence=min_evidence,
        top_n=15,
        include_rates=True,
    )
    candidates = _flatten_candidates(compass)
    thin = _is_thin(compass, candidates, owned)
    coverage = {
        "owned_skill_count": len(owned),
        "candidate_count": len(candidates),
        "thin": thin,
        "lens": compass.get("lens") or lens or "all",
        "period_days": days,
        "score_version": compass.get("score_version"),
    }
    limits = _collect_limits(compass, candidates)
    if thin:
        limits = list(limits) + [
            "Evidence thin or profile incomplete; plan will be stub / coverage-only."
        ]
    busy = normalize_busy_slots(busy_slots)
    return {
        "modality": modality,
        "hours_per_week": hours_per_week,
        "horizon_weeks": horizon_weeks,
        "skills": owned,
        "certifications": list(certifications or []),
        "busy_slots": busy,
        "coverage": coverage,
        "candidates": candidates[:12],
        "related_certifications": compass.get("related_certifications")
        or (compass.get("market") or {}).get("related_certifications")
        or [],
        "limits": limits,
        "disclaimer": compass.get("disclaimer")
        or "Observed corpus only; not market size or ROI.",
        "methodology_version": get_settings().methodology_version,
    }


def _flatten_candidates(compass: dict[str, Any]) -> list[dict[str, Any]]:
    if compass.get("lens") == "compare":
        items: list[dict[str, Any]] = []
        for side in ("market", "focus"):
            for c in (compass.get(side) or {}).get("candidates") or []:
                row = dict(c)
                row["_lens_side"] = side
                items.append(row)
        return items
    return list(compass.get("candidates") or [])


def _is_thin(
    compass: dict[str, Any],
    candidates: list[dict[str, Any]],
    owned: list[str],
) -> bool:
    if compass.get("error"):
        return True
    if len(owned) < 3:
        return True
    if not candidates:
        return True
    status = compass.get("status") or (compass.get("market") or {}).get("status")
    if status == "insufficient_data":
        return True
    return False


def _collect_limits(compass: dict[str, Any], candidates: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for key in ("limits", "disclaimer"):
        val = compass.get(key)
        if isinstance(val, list):
            out.extend(str(x) for x in val if x)
        elif isinstance(val, str) and val:
            out.append(val)
    for c in candidates[:5]:
        lim = c.get("limits")
        if isinstance(lim, list):
            out.extend(str(x) for x in lim if x)
        elif isinstance(lim, str) and lim:
            out.append(lim)
    # de-dupe preserving order
    seen: set[str] = set()
    uniq: list[str] = []
    for x in out:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq[:20]


def stub_study_plan(evidence: dict[str, Any]) -> StudyPlan:
    modality: Modality = evidence.get("modality") or "employed_part_time"
    hours = float(evidence.get("hours_per_week") or 6)
    horizon = int(evidence.get("horizon_weeks") or 8)
    candidates = evidence.get("candidates") or []
    stack = [str(c.get("technology")) for c in candidates[:3] if c.get("technology")]
    milestones: list[StudyMilestone] = []
    for i, tech in enumerate(stack[:2], start=1):
        milestones.append(
            StudyMilestone(
                week=min(i * 2, horizon),
                title=f"Learn {tech}",
                skills=[tech],
                evidence_refs=[f"candidate:{tech}"],
                hours=hours * 2,
            )
        )
    limits = list(evidence.get("limits") or [])
    if evidence.get("coverage", {}).get("thin"):
        limits = limits + ["insufficient_data: stub plan from observed candidates only"]
    if not stack:
        limits = limits + ["No learning candidates; empty stack_target"]
    schedule = build_weekly_schedule(
        hours_per_week=hours,
        modality=modality,
        busy_slots=evidence.get("busy_slots"),
    )
    limits = limits + list(schedule.get("notes") or [])
    return StudyPlan(
        title="Study plan (deterministic stub)",
        horizon_weeks=horizon,
        modality=modality,
        hours_per_week=hours,
        stack_target=stack,
        milestones=milestones,
        weekly_template=list(schedule.get("weekly_template") or []),
        limits=limits,
        source="stub",
    )


def validate_plan_against_evidence(plan: StudyPlan, evidence: dict[str, Any]) -> StudyPlan:
    allowed = {
        str(c.get("technology")).strip()
        for c in (evidence.get("candidates") or [])
        if c.get("technology")
    }
    owned = {str(s).strip() for s in (evidence.get("skills") or []) if s}
    known = allowed | owned
    cleaned_stack = [s for s in plan.stack_target if s in known]
    cleaned_ms: list[StudyMilestone] = []
    for m in plan.milestones:
        skills = [s for s in m.skills if s in known]
        if not skills and m.skills:
            continue
        refs = m.evidence_refs or [f"candidate:{s}" for s in skills]
        cleaned_ms.append(
            m.model_copy(update={"skills": skills, "evidence_refs": refs})
        )
    limits = list(plan.limits)
    dropped = set(plan.stack_target) - set(cleaned_stack)
    if dropped:
        limits.append(f"Dropped ungrounded stack items: {sorted(dropped)}")
    cleaned = plan.model_copy(
        update={
            "stack_target": cleaned_stack,
            "milestones": cleaned_ms,
            "limits": limits,
        }
    )
    return _attach_calendar(cleaned, evidence)


async def generate_study_plan(db: Session, evidence: dict[str, Any]) -> dict[str, Any]:
    stub = stub_study_plan(evidence)
    thin = bool(evidence.get("coverage", {}).get("thin"))
    cfg = resolve_llm_settings(db)
    provider = get_llm_provider(db)
    health = await provider.health()
    use_llm = (
        not thin
        and cfg.provider != "none"
        and cfg.enable_study_advisor
        and health.get("healthy")
        and provider.name != "none"
    )
    if not use_llm:
        reason = "thin_or_llm_off"
        if thin:
            reason = "insufficient_data"
        elif cfg.provider == "none" or not cfg.enable_study_advisor:
            reason = "llm_disabled"
        return {
            "status": "ok",
            "mode": "stub",
            "reason": reason,
            "plan": _attach_calendar(stub, evidence).model_dump(),
            "evidence": evidence,
            "llm_health": health,
        }

    try:
        prompt = resolve_prompt(
            db,
            slug="study_plan",
            variables={
                "modality": str(evidence.get("modality")),
                "hours_per_week": str(evidence.get("hours_per_week")),
                "horizon_weeks": str(evidence.get("horizon_weeks")),
                "evidence_json": compact_evidence_for_llm(evidence),
            },
        )
        raw = await provider.chat(
            [
                {"role": "system", "content": prompt["system"]},
                {"role": "user", "content": prompt["user"]},
            ],
            response_json=True,
        )
        data = json.loads(raw or "{}")
        if not isinstance(data, dict):
            raise ValueError("LLM study plan was not a JSON object")
        data = coerce_llm_plan_payload(data, evidence=evidence)
        data["source"] = "llm"
        plan = StudyPlan.model_validate(data)
        plan = validate_plan_against_evidence(plan, evidence)
        plan = _attach_calendar(plan, evidence)
        return {
            "status": "ok",
            "mode": "llm",
            "plan": plan.model_dump(),
            "evidence": evidence,
            "prompt_version": prompt.get("version"),
            "llm_health": health,
        }
    except (ValidationError, json.JSONDecodeError, Exception) as exc:  # noqa: BLE001
        fallback = _attach_calendar(
            stub.model_copy(update={"limits": stub.limits + [f"LLM fallback: {exc}"]}),
            evidence,
        )
        return {
            "status": "ok",
            "mode": "stub",
            "reason": "llm_error",
            "plan": fallback.model_dump(),
            "evidence": evidence,
            "llm_health": health,
            "error": str(exc),
        }


async def refine_study_plan(
    db: Session,
    *,
    plan: dict[str, Any],
    evidence: dict[str, Any],
    user_message: str,
) -> dict[str, Any]:
    cfg = resolve_llm_settings(db)
    provider = get_llm_provider(db)
    health = await provider.health()
    if (
        cfg.provider == "none"
        or not cfg.enable_study_advisor
        or not health.get("healthy")
        or provider.name == "none"
    ):
        return {
            "status": "skipped",
            "reason": "llm_disabled",
            "plan": plan,
            "llm_health": health,
        }
    try:
        prompt = resolve_prompt(
            db,
            slug="study_refine",
            variables={
                "plan_json": json.dumps(plan, default=str, separators=(",", ":"))[:4000],
                "evidence_json": compact_evidence_for_llm(evidence, max_chars=3500),
                "user_message": user_message[:500],
            },
        )
        raw = await provider.chat(
            [
                {"role": "system", "content": prompt["system"]},
                {"role": "user", "content": prompt["user"]},
            ],
            response_json=True,
        )
        patch = json.loads(raw or "{}")
        merged = {**plan, **{k: v for k, v in patch.items() if v is not None}}
        merged["source"] = "llm_refine"
        validated = StudyPlan.model_validate(merged)
        validated = validate_plan_against_evidence(validated, evidence)
        return {
            "status": "ok",
            "mode": "llm_refine",
            "plan": validated.model_dump(),
            "prompt_version": prompt.get("version"),
            "llm_health": health,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "error",
            "error": str(exc),
            "plan": plan,
            "llm_health": health,
        }
