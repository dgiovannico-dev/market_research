from __future__ import annotations

from datetime import date
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.outcomes import outcomes_summary
from app.analytics.positioning import recommendations, skill_gaps
from app.api.deps import verify_api_key
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


@router.get("/profile/skill-gaps")
def profile_skill_gaps(
    db: Session = Depends(get_db),
    country_code: Optional[str] = Query(
        default=None,
        description="Optional CSV ISO country codes (same as market KPIs).",
    ),
) -> dict[str, Any]:
    return skill_gaps(db, country_code=country_code)


@router.get("/profile/recommendations")
def profile_recommendations(
    db: Session = Depends(get_db),
    country_code: Optional[str] = Query(
        default=None,
        description="Optional CSV ISO country codes (same as market KPIs).",
    ),
) -> dict[str, Any]:
    return recommendations(db, country_code=country_code)


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
