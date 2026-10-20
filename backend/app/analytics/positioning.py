from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.storage.models import Job, JobSkill, Technology, UserProfile, UserSkill


def skill_gaps(db: Session, *, days: int = 90) -> dict[str, Any]:
    profile = db.scalar(select(UserProfile).order_by(UserProfile.id).limit(1))
    if not profile:
        return {"error": "profile_missing"}

    user_tech_ids = set(
        db.scalars(select(UserSkill.technology_id).where(UserSkill.profile_id == profile.id)).all()
    )
    user_names = {
        t.canonical_name
        for t in db.scalars(select(Technology).where(Technology.id.in_(user_tech_ids or [-1]))).all()
    }

    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=days)
    demand = db.execute(
        select(
            Technology.id,
            Technology.canonical_name,
            JobSkill.importance,
            func.count(JobSkill.id),
        )
        .join(JobSkill, JobSkill.technology_id == Technology.id)
        .join(Job, Job.id == JobSkill.job_id)
        .where(Job.is_canonical.is_(True), Job.published_at >= date_from)
        .group_by(Technology.id, Technology.canonical_name, JobSkill.importance)
    ).all()

    agg: dict[str, dict[str, Any]] = {}
    for tech_id, name, importance, count in demand:
        row = agg.setdefault(
            name,
            {
                "technology": name,
                "technology_id": tech_id,
                "owned": name in user_names,
                "required_mentions": 0,
                "preferred_mentions": 0,
                "mentioned_mentions": 0,
            },
        )
        key = f"{importance}_mentions"
        if key in row:
            row[key] += count

    weights = profile.skill_priority_weights or {}
    gaps = []
    for name, row in agg.items():
        if row["owned"]:
            continue
        demand_score = row["required_mentions"] * 1.5 + row["preferred_mentions"] + row["mentioned_mentions"] * 0.5
        score = (
            demand_score * float(weights.get("demand", 0.25))
            + (1 if row["required_mentions"] else 0) * float(weights.get("compatibility", 0.2))
        )
        gap_type = (
            "required_missing"
            if row["required_mentions"]
            else "preferred_missing"
            if row["preferred_mentions"]
            else "mentioned_missing"
        )
        gaps.append(
            {
                **row,
                "gap_type": gap_type,
                "priority_score": round(score, 3),
                "evidence_kind": "derived",
                "limits": "Based on observed job skill mentions vs configured profile skills. Not earnings guarantee.",
            }
        )
    gaps.sort(key=lambda x: -x["priority_score"])

    accessible = db.scalar(
        select(func.count())
        .select_from(Job)
        .where(
            Job.is_canonical.is_(True),
            Job.published_at >= date_from,
            Job.remote_type == "remote",
            Job.contract_type.in_(["freelance", "b2b", "contractor"]),
        )
    ) or 0

    return {
        "profile_id": profile.id,
        "residence_country": profile.residence_country,
        "owned_skills": sorted(user_names),
        "weights": weights,
        "accessible_remote_b2b_jobs_observed": accessible,
        "gaps": gaps[:50],
        "disclaimer": "Recommendations are observational gap analysis, not promises of revenue.",
    }


def recommendations(db: Session, *, days: int = 60, limit: int = 25) -> dict[str, Any]:
    profile = db.scalar(select(UserProfile).order_by(UserProfile.id).limit(1))
    if not profile:
        return {"error": "profile_missing", "items": []}
    user_tech = set(
        db.scalars(
            select(Technology.canonical_name)
            .join(UserSkill, UserSkill.technology_id == Technology.id)
            .where(UserSkill.profile_id == profile.id)
        ).all()
    )
    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=days)
    jobs = db.scalars(
        select(Job)
        .options(joinedload(Job.skills).joinedload(JobSkill.technology), joinedload(Job.rates))
        .where(
            Job.is_canonical.is_(True),
            Job.published_at >= date_from,
            Job.contract_type.in_(["freelance", "b2b", "contractor", "unknown"]),
        )
        .order_by(Job.published_at.desc())
        .limit(300)
    ).unique().all()

    items = []
    for job in jobs:
        names = {s.technology.canonical_name for s in job.skills if s.technology}
        if not names:
            continue
        overlap = names & user_tech
        missing_required = {
            s.technology.canonical_name
            for s in job.skills
            if s.technology and s.importance == "required" and s.technology.canonical_name not in user_tech
        }
        match = len(overlap) / len(names)
        geo_ok = job.residence_restriction != "explicitly_restricted"
        items.append(
            {
                "job_id": job.id,
                "title": job.title_original,
                "country_code": job.country_code,
                "contract_type": job.contract_type,
                "remote_type": job.remote_type,
                "skill_match": round(match, 3),
                "overlap_skills": sorted(overlap),
                "missing_required_skills": sorted(missing_required),
                "residence_restriction": job.residence_restriction,
                "geo_accessible_heuristic": geo_ok,
                "canonical_url": job.canonical_url,
                "evidence_kind": "derived",
            }
        )
    items.sort(key=lambda x: (-x["skill_match"], -len(x["overlap_skills"])))
    return {
        "profile_id": profile.id,
        "period_days": days,
        "items": items[:limit],
        "disclaimer": "Match is overlap of configured skills vs extracted job skills.",
    }
