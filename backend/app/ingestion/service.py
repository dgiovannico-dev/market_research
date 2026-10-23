from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.classification import TAXONOMY, classify_job
from app.collectors.base import RawJob
from app.normalization.country_codes import country_code_from_collector_raw
from app.ingestion.evidence_tier import resolve_evidence_tier, source_snapshot_at_from_raw
from app.ingestion.job_skills import sync_job_rates, sync_job_skills
from app.ingestion.snapshots import maybe_add_snapshot
from app.normalization.hashing import content_hash, normalize_text
from app.normalization.url import canonicalize_url
from app.storage.models import Job, JobIntentMatch, Technology

# Mirror DB varchar limits so a long collector field cannot abort the whole flush.
_EMPLOYMENT_TYPE_MAX = 64


def _clip(value: str | None, max_len: int) -> str | None:
    if value is None:
        return None
    text = str(value)
    if len(text) <= max_len:
        return text
    return text[:max_len]


def _apply_remote_hint(classified_remote: str, remote_hint: bool | str | None) -> str:
    """Map RawJob.remote_hint onto classified remote_type when still unknown."""
    if classified_remote != "unknown" or remote_hint in (None, False, ""):
        return classified_remote
    if isinstance(remote_hint, str):
        hint = remote_hint.strip().lower()
        if hint in {"remote", "hybrid", "onsite"}:
            return hint
        return "remote"
    return "remote"


def ensure_taxonomy(db: Session) -> dict[str, Technology]:
    existing = {t.canonical_name: t for t in db.scalars(select(Technology)).all()}
    for item in TAXONOMY:
        if item["canonical_name"] not in existing:
            tech = Technology(
                canonical_name=item["canonical_name"],
                category=item["category"],
                aliases=item.get("aliases", []),
            )
            db.add(tech)
            db.flush()
            existing[tech.canonical_name] = tech
    return existing


def find_duplicate(
    db: Session,
    *,
    source_id: int,
    source_job_id: str,
    canonical_url: str,
    description_hash: str | None,
) -> Job | None:
    by_native = db.scalar(
        select(Job).where(Job.source_id == source_id, Job.source_job_id == source_job_id)
    )
    if by_native:
        return by_native
    if canonical_url:
        by_url = db.scalar(
            select(Job).where(Job.canonical_url == canonical_url, Job.is_canonical.is_(True))
        )
        if by_url:
            return by_url
    if description_hash:
        by_hash = db.scalar(
            select(Job).where(
                Job.description_hash == description_hash,
                Job.is_canonical.is_(True),
            )
        )
        if by_hash:
            return by_hash
    return None


def upsert_raw_job(
    db: Session,
    *,
    source_id: int,
    raw: RawJob,
    query_id: Optional[int] = None,
    collection_method: str = "api",
    tech_map: Optional[dict[str, Technology]] = None,
) -> tuple[Job, str]:
    """Returns (job, action) where action is inserted|updated|duplicate."""
    if not (raw.url or "").strip():
        raise ValueError("empty_url")
    tech_map = tech_map if tech_map is not None else ensure_taxonomy(db)
    url = canonicalize_url(raw.url)
    if not url or url == "/":
        raise ValueError("empty_url")
    desc_hash = content_hash(raw.description)
    now = datetime.now(timezone.utc)
    existing = find_duplicate(
        db,
        source_id=source_id,
        source_job_id=raw.source_job_id,
        canonical_url=url,
        description_hash=desc_hash,
    )
    classified = classify_job(
        title=raw.title,
        description=raw.description,
        location=raw.location,
        salary_text=raw.salary_text,
        tags=raw.tags,
        job_type=raw.job_type,
    )
    classified.remote_type = _apply_remote_hint(classified.remote_type, raw.remote_hint)

    # Collectors may tag ISO country on raw; prefer over location text heuristics.
    tagged_country = country_code_from_collector_raw(raw.raw)
    if tagged_country:
        classified.country_code = tagged_country

    tier = resolve_evidence_tier(raw)
    snap_at = source_snapshot_at_from_raw(raw)

    if existing:
        existing.last_seen_at = now
        existing.title_original = raw.title
        existing.description_original = raw.description
        existing.description_hash = desc_hash
        existing.location_original = raw.location
        existing.country_code = classified.country_code or existing.country_code
        existing.remote_type = classified.remote_type
        existing.employment_type = _clip(raw.job_type, _EMPLOYMENT_TYPE_MAX) or existing.employment_type
        existing.contract_type = classified.contract_type
        existing.contract_type_confidence = classified.contract_type_confidence
        existing.contract_evidence_kind = classified.contract_evidence_kind
        existing.b2b_eligible = classified.b2b_eligible
        existing.b2b_evidence = classified.b2b_evidence
        existing.residence_restriction = classified.residence_restriction
        existing.seniority = classified.seniority
        existing.role_family = classified.role_family
        existing.language_requirements = list(classified.language_requirements or [])
        existing.classification_version = classified.classification_version
        existing.evidence_tier = tier
        if snap_at is not None:
            existing.source_snapshot_at = snap_at
        # Re-open soft-expired rows when the source still lists them.
        if existing.status in ("closed_stale", "stale", "closed"):
            existing.status = "active_unverified"
            existing.closed_at = None
        action = "updated"
        if existing.source_id != source_id or existing.source_job_id != raw.source_job_id:
            action = "duplicate"
            existing.is_canonical = True
        job = existing
        if query_id is not None and job.query_id is None:
            job.query_id = query_id
    else:
        job = Job(
            source_id=source_id,
            query_id=query_id,
            source_job_id=raw.source_job_id,
            canonical_url=url,
            title_original=raw.title,
            title_normalized=normalize_text(raw.title),
            company_original=raw.company,
            company_normalized=normalize_text(raw.company),
            description_original=raw.description,
            description_hash=desc_hash,
            location_original=raw.location,
            country_code=classified.country_code,
            remote_type=classified.remote_type,
            employment_type=_clip(raw.job_type, _EMPLOYMENT_TYPE_MAX),
            contract_type=classified.contract_type,
            contract_type_confidence=classified.contract_type_confidence,
            contract_evidence_kind=classified.contract_evidence_kind,
            b2b_eligible=classified.b2b_eligible,
            b2b_evidence=classified.b2b_evidence,
            residence_restriction=classified.residence_restriction,
            seniority=classified.seniority,
            role_family=classified.role_family,
            language_requirements=list(classified.language_requirements or []),
            published_at=raw.published_at,
            first_seen_at=now,
            last_seen_at=now,
            status="active_unverified",
            collection_method=collection_method,
            evidence_tier=tier,
            source_snapshot_at=snap_at,
            classification_version=classified.classification_version,
            is_canonical=True,
        )
        db.add(job)
        db.flush()
        action = "inserted"

    sync_job_skills(
        db, job, classified_techs=classified.technologies, tech_map=tech_map
    )
    sync_job_rates(db, job, classified_rate=classified.rate or None)

    maybe_add_snapshot(
        db,
        job=job,
        observed_at=now,
        description_hash=desc_hash,
        rate_evidence=classified.rate.get("evidence_text") if classified.rate else None,
    )
    if query_id is not None:
        upsert_intent_match(db, job_id=job.id, query_id=query_id, matched_at=now)
    db.flush()
    return job, action


def upsert_intent_match(
    db: Session,
    *,
    job_id: int,
    query_id: int,
    matched_at: Optional[datetime] = None,
) -> str:
    """Idempotent job↔intent provenance. Returns ``created`` or ``updated``."""
    now = matched_at or datetime.now(timezone.utc)
    existing = db.scalar(
        select(JobIntentMatch).where(
            JobIntentMatch.job_id == job_id, JobIntentMatch.query_id == query_id
        )
    )
    if existing:
        existing.last_matched_at = now
        return "updated"
    db.add(
        JobIntentMatch(
            job_id=job_id,
            query_id=query_id,
            first_matched_at=now,
            last_matched_at=now,
        )
    )
    return "created"


def ingest_raw_jobs(
    db: Session,
    *,
    source_id: int,
    raw_jobs: list[RawJob],
    query_id: Optional[int] = None,
    collection_method: str = "api",
) -> dict[str, Any]:
    stats = {"inserted": 0, "updated": 0, "duplicates": 0, "errors": 0}
    tech_map = ensure_taxonomy(db) if raw_jobs else {}
    for raw in raw_jobs:
        try:
            # SAVEPOINT: one bad row must not poison the whole Session (PendingRollback).
            with db.begin_nested():
                _, action = upsert_raw_job(
                    db,
                    source_id=source_id,
                    raw=raw,
                    query_id=query_id,
                    collection_method=collection_method,
                    tech_map=tech_map,
                )
            stats[
                {"inserted": "inserted", "updated": "updated", "duplicate": "duplicates"}[
                    action
                ]
            ] += 1
        except Exception:  # noqa: BLE001
            stats["errors"] += 1
    db.commit()
    return stats
