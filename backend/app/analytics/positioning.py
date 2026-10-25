from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.analytics.country_filter import parse_country_codes
from app.analytics.job_query import base_job_query
from app.analytics.skill_ownership import names_match_owned, resolve_owned_skill_names
from app.storage.models import Job, JobSkill, Technology, UserProfile, UserSkill


def skill_gaps(
    db: Session,
    *,
    days: int = 90,
    country_code: Optional[str] = None,
    owned_skills: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Gap analysis vs observed demand.

    When ``owned_skills`` is provided (localStorage / client profile), skip DB
    UserProfile. Otherwise fall back to first profile row (legacy).
    """
    profile: UserProfile | None = None
    weights: dict[str, Any] = {}
    if owned_skills is not None:
        user_names = resolve_owned_skill_names(owned_skills)
        profile_id = None
        residence = None
    else:
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
        weights = profile.skill_priority_weights or {}
        profile_id = profile.id
        residence = profile.residence_country

    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=days)
    codes = parse_country_codes(country_code)
    corpus = base_job_query(date_from=date_from, country_codes=codes)
    job_ids = select(corpus.with_only_columns(Job.id).subquery().c.id)
    demand = db.execute(
        select(
            Technology.id,
            Technology.canonical_name,
            JobSkill.importance,
            func.count(JobSkill.id),
        )
        .join(JobSkill, JobSkill.technology_id == Technology.id)
        .join(Job, Job.id == JobSkill.job_id)
        .where(Job.id.in_(job_ids))
        .group_by(Technology.id, Technology.canonical_name, JobSkill.importance)
    ).all()

    agg: dict[str, dict[str, Any]] = {}
    for tech_id, name, importance, count in demand:
        row = agg.setdefault(
            name,
            {
                "technology": name,
                "technology_id": tech_id,
                "owned": names_match_owned(name, user_names),
                "required_mentions": 0,
                "preferred_mentions": 0,
                "mentioned_mentions": 0,
            },
        )
        key = f"{importance}_mentions"
        if key in row:
            row[key] += count

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

    accessible_q = base_job_query(
        date_from=date_from,
        country_codes=codes,
        remote_type="remote",
        verified_contract_only=True,
    )
    accessible = db.scalar(select(func.count()).select_from(accessible_q.subquery())) or 0

    return {
        "profile_id": profile_id,
        "residence_country": residence,
        "countries": codes or None,
        "owned_skills": sorted(user_names),
        "weights": weights,
        "accessible_remote_b2b_jobs_observed": accessible,
        "gaps": gaps[:50],
        "disclaimer": "Recommendations are observational gap analysis, not promises of revenue.",
        "source": "client_skills" if owned_skills is not None else "db_profile",
    }


def recommendations(
    db: Session,
    *,
    days: int = 60,
    limit: int = 25,
    country_code: Optional[str] = None,
    owned_skills: Optional[list[str]] = None,
) -> dict[str, Any]:
    profile: UserProfile | None = None
    if owned_skills is not None:
        user_tech = resolve_owned_skill_names(owned_skills)
        profile_id = None
    else:
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
        profile_id = profile.id
    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=days)
    codes = parse_country_codes(country_code)
    corpus = base_job_query(date_from=date_from, country_codes=codes)
    jobs = db.scalars(
        select(Job)
        .options(joinedload(Job.skills).joinedload(JobSkill.technology), joinedload(Job.rates))
        .where(
            Job.id.in_(corpus.with_only_columns(Job.id)),
            Job.contract_type.in_(["freelance", "b2b", "contractor", "unknown"]),
        )
        .order_by(Job.published_at.desc())
        .limit(300)
    ).unique().all()

    items: list[dict[str, Any]] = []
    for job in jobs:
        names = {s.technology.canonical_name for s in job.skills if s.technology}
        if not names:
            continue
        overlap = {n for n in names if names_match_owned(n, user_tech)}
        if not overlap:
            # Zero-overlap rows look like spam duplicates in the UI; skip them.
            continue
        missing_required = {
            s.technology.canonical_name
            for s in job.skills
            if s.technology
            and s.importance == "required"
            and not names_match_owned(s.technology.canonical_name, user_tech)
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
    # Deduplicate identical titles (same posting mirrored across sources/days).
    deduped: list[dict[str, Any]] = []
    seen_titles: set[str] = set()
    for item in items:
        key = " ".join(str(item.get("title") or "").lower().split())
        if not key or key in seen_titles:
            continue
        seen_titles.add(key)
        deduped.append(item)
        if len(deduped) >= limit:
            break
    return {
        "profile_id": profile_id,
        "period_days": days,
        "countries": codes or None,
        "items": deduped,
        "disclaimer": "Match is overlap of configured skills vs extracted job skills.",
        "source": "client_skills" if owned_skills is not None else "db_profile",
    }
