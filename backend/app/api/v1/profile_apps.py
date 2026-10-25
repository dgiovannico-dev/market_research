from __future__ import annotations

from datetime import date
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.learning_candidates import learning_candidates
from app.analytics.outcomes import outcomes_summary
from app.analytics.positioning import recommendations, skill_gaps
from app.analytics.study_advice import (
    build_evidence_pack,
    generate_study_plan,
    refine_study_plan,
)
from app.api.deps import verify_api_key
from app.api.v1.query_params import min_evidence_query, parse_lens_params
from app.storage.db import get_db
from app.storage.models import ApplicationOutcome, Technology, UserProfile, UserSkill

router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])


class ProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    years_experience: Optional[int] = None
    residence_country: Optional[str] = None
    languages: Optional[list[str]] = None
    remote_preference: Optional[str] = None
    contract_preference: Optional[list[str]] = None
    min_rate_amount: Optional[float] = None
    target_rate_amount: Optional[float] = None
    rate_unit: Optional[str] = None
    rate_currency: Optional[str] = None
    skill_priority_weights: Optional[dict[str, float]] = None
    skills: Optional[list[str]] = Field(
        default=None, description="Canonical technology names to set as owned skills"
    )


class ApplicationCreate(BaseModel):
    job_id: Optional[int] = None
    applied_at: date
    channel: Optional[str] = None
    intermediary: Optional[str] = None
    requested_rate: Optional[float] = None
    offered_rate: Optional[float] = None
    rate_unit: Optional[str] = None
    currency: Optional[str] = None
    response: Optional[str] = None
    interview: Optional[bool] = None
    outcome: Optional[str] = None
    rejection_reason: Optional[str] = None
    notes: Optional[str] = None


def _profile(db: Session) -> UserProfile:
    profile = db.scalar(select(UserProfile).order_by(UserProfile.id).limit(1))
    if not profile:
        raise HTTPException(404, "Profile not found")
    return profile


@router.put("/profile")
def update_profile(payload: ProfileUpdate, db: Session = Depends(get_db)) -> dict[str, Any]:
    profile = _profile(db)
    data = payload.model_dump(exclude_unset=True)
    skills = data.pop("skills", None)
    for key, value in data.items():
        setattr(profile, key, value)
    if skills is not None:
        existing = db.scalars(select(UserSkill).where(UserSkill.profile_id == profile.id)).all()
        for row in existing:
            db.delete(row)
        for name in skills:
            tech = db.scalar(select(Technology).where(Technology.canonical_name == name))
            if not tech:
                continue
            db.add(UserSkill(profile_id=profile.id, technology_id=tech.id, level="advanced"))
    db.commit()
    return {"status": "updated", "id": profile.id}


class DashboardPrefsBody(BaseModel):
    prefs: dict[str, Any]


@router.get("/profile/dashboard-prefs")
def get_dashboard_prefs(db: Session = Depends(get_db)) -> dict[str, Any]:
    profile = _profile(db)
    return {"prefs": profile.dashboard_prefs or {}, "profile_id": profile.id}


@router.put("/profile/dashboard-prefs")
def put_dashboard_prefs(body: DashboardPrefsBody, db: Session = Depends(get_db)) -> dict[str, Any]:
    profile = _profile(db)
    profile.dashboard_prefs = body.prefs
    db.commit()
    return {"status": "saved", "profile_id": profile.id, "prefs": profile.dashboard_prefs}


class SkillsBody(BaseModel):
    """Client localStorage profile skills (ADR-009)."""

    skills: list[str] = Field(default_factory=list)
    country_code: Optional[str] = None
    days: Optional[int] = None


class LearningCandidatesBody(BaseModel):
    """Stack Compass learning candidates (SPEC-stack-compass)."""

    skills: list[str] = Field(default_factory=list)
    certifications: Optional[list[str]] = None
    country_code: Optional[str] = None
    days: Optional[int] = None
    top_n: Optional[int] = Field(default=15, ge=1, le=50)
    include_rates: bool = True


@router.get("/profile/skill-gaps")
def profile_skill_gaps(
    db: Session = Depends(get_db),
    country_code: Optional[str] = Query(
        default=None,
        description="Optional CSV ISO country codes (same as market KPIs).",
    ),
) -> dict[str, Any]:
    return skill_gaps(db, country_code=country_code)


@router.post("/profile/skill-gaps")
def profile_skill_gaps_from_skills(
    body: SkillsBody,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return skill_gaps(
        db,
        country_code=body.country_code,
        days=body.days or 90,
        owned_skills=body.skills,
    )


@router.get("/profile/recommendations")
def profile_recommendations(
    db: Session = Depends(get_db),
    country_code: Optional[str] = Query(
        default=None,
        description="Optional CSV ISO country codes (same as market KPIs).",
    ),
) -> dict[str, Any]:
    return recommendations(db, country_code=country_code)


@router.post("/profile/recommendations")
def profile_recommendations_from_skills(
    body: SkillsBody,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return recommendations(
        db,
        country_code=body.country_code,
        days=body.days or 60,
        owned_skills=body.skills,
    )


@router.post("/profile/learning-candidates")
def profile_learning_candidates(
    body: LearningCandidatesBody,
    db: Session = Depends(get_db),
    lens: Optional[str] = Query(None, description="Omit for all jobs; market|focus|compare."),
    query_ids: Optional[list[str]] = Query(None),
    min_evidence: Optional[str] = Query(
        None,
        description="Corpus gate: standard (default), all, or thin.",
    ),
) -> dict[str, Any]:
    """Complementary scarce skills to learn next (gaps + co-occurrence + score)."""
    lens_name, qids = parse_lens_params(lens, query_ids)
    return learning_candidates(
        db,
        owned_skills=body.skills,
        owned_certifications=body.certifications,
        days=body.days or 90,
        country_code=body.country_code,
        lens=lens_name,
        query_ids=qids,
        min_evidence=min_evidence_query(min_evidence),
        top_n=body.top_n or 15,
        include_rates=body.include_rates,
    )


class StudyEvidenceBody(BaseModel):
    skills: list[str] = Field(default_factory=list)
    certifications: Optional[list[str]] = None
    hours_per_week: float = Field(default=6, gt=0, le=80)
    modality: str = Field(default="employed_part_time")
    horizon_weeks: int = Field(default=8, ge=1, le=52)
    country_code: Optional[str] = None
    days: Optional[int] = None


class StudyPlanBody(StudyEvidenceBody):
    pass


class StudyRefineBody(BaseModel):
    plan: dict[str, Any]
    evidence: dict[str, Any]
    message: str = Field(min_length=1, max_length=2000)


@router.post("/profile/study-advice/evidence")
def study_advice_evidence(
    body: StudyEvidenceBody,
    db: Session = Depends(get_db),
    lens: Optional[str] = Query(None),
    query_ids: Optional[list[str]] = Query(None),
    min_evidence: Optional[str] = Query(None),
) -> dict[str, Any]:
    modality = body.modality
    if modality not in (
        "employed_part_time",
        "freelance_full_time",
        "intensive",
    ):
        raise HTTPException(400, "invalid modality")
    lens_name, qids = parse_lens_params(lens, query_ids)
    return build_evidence_pack(
        db,
        skills=body.skills,
        certifications=body.certifications,
        hours_per_week=body.hours_per_week,
        modality=modality,  # type: ignore[arg-type]
        horizon_weeks=body.horizon_weeks,
        days=body.days or 90,
        country_code=body.country_code,
        lens=lens_name,
        query_ids=qids,
        min_evidence=min_evidence_query(min_evidence),
    )


@router.post("/profile/study-advice/plan")
async def study_advice_plan(
    body: StudyPlanBody,
    db: Session = Depends(get_db),
    lens: Optional[str] = Query(None),
    query_ids: Optional[list[str]] = Query(None),
    min_evidence: Optional[str] = Query(None),
) -> dict[str, Any]:
    modality = body.modality
    if modality not in (
        "employed_part_time",
        "freelance_full_time",
        "intensive",
    ):
        raise HTTPException(400, "invalid modality")
    lens_name, qids = parse_lens_params(lens, query_ids)
    evidence = build_evidence_pack(
        db,
        skills=body.skills,
        certifications=body.certifications,
        hours_per_week=body.hours_per_week,
        modality=modality,  # type: ignore[arg-type]
        horizon_weeks=body.horizon_weeks,
        days=body.days or 90,
        country_code=body.country_code,
        lens=lens_name,
        query_ids=qids,
        min_evidence=min_evidence_query(min_evidence),
    )
    return await generate_study_plan(db, evidence)


@router.post("/profile/study-advice/refine")
async def study_advice_refine(
    body: StudyRefineBody,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return await refine_study_plan(
        db,
        plan=body.plan,
        evidence=body.evidence,
        user_message=body.message,
    )


@router.get("/applications")
def list_applications(db: Session = Depends(get_db)) -> dict[str, Any]:
    profile = _profile(db)
    rows = db.scalars(
        select(ApplicationOutcome)
        .where(ApplicationOutcome.profile_id == profile.id)
        .order_by(ApplicationOutcome.applied_at.desc())
    ).all()
    return {
        "items": [
            {
                "id": r.id,
                "job_id": r.job_id,
                "applied_at": r.applied_at.isoformat(),
                "channel": r.channel,
                "requested_rate": r.requested_rate,
                "offered_rate": r.offered_rate,
                "response": r.response,
                "interview": r.interview,
                "outcome": r.outcome,
                "rejection_reason": r.rejection_reason,
            }
            for r in rows
        ],
        "summary": outcomes_summary(db, profile.id),
    }


@router.post("/applications")
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)) -> dict[str, Any]:
    profile = _profile(db)
    row = ApplicationOutcome(profile_id=profile.id, **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "status": "created"}
