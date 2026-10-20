from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.classification.rules import classify_job
from app.classification.taxonomy import TAXONOMY
from app.collectors.base import RawJob
from app.normalization.hashing import content_hash, normalize_text
from app.normalization.url import canonicalize_url
from app.storage.models import Job, JobRate, JobSkill, JobSnapshot, Technology


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
    by_url = db.scalar(select(Job).where(Job.canonical_url == canonical_url, Job.is_canonical.is_(True)))
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
) -> tuple[Job, str]:
    """Returns (job, action) where action is inserted|updated|duplicate."""
    tech_map = ensure_taxonomy(db)
    url = canonicalize_url(raw.url)
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
    if raw.remote_hint and classified.remote_type == "unknown":
        classified.remote_type = "remote"

    if existing:
        existing.last_seen_at = now
        existing.title_original = raw.title
        existing.description_original = raw.description
        existing.description_hash = desc_hash
        existing.location_original = raw.location
        existing.country_code = classified.country_code or existing.country_code
        existing.remote_type = classified.remote_type
        existing.contract_type = classified.contract_type
        existing.contract_type_confidence = classified.contract_type_confidence
        existing.contract_evidence_kind = classified.contract_evidence_kind
        existing.b2b_eligible = classified.b2b_eligible
        existing.b2b_evidence = classified.b2b_evidence
        existing.residence_restriction = classified.residence_restriction
        existing.seniority = classified.seniority
        existing.role_family = classified.role_family
        existing.classification_version = classified.classification_version
        action = "updated"
        if existing.source_id != source_id or existing.source_job_id != raw.source_job_id:
            action = "duplicate"
            existing.is_canonical = True
        job = existing
    else:
        job = Job(
            source_id=source_id,
            query_id=query_id,
            source_job_id=raw.source_job_id,
            canonical_url=url or f"missing://{source_id}/{raw.source_job_id}",
            title_original=raw.title,
            title_normalized=normalize_text(raw.title),
            company_original=raw.company,
            company_normalized=normalize_text(raw.company),
            description_original=raw.description,
            description_hash=desc_hash,
            location_original=raw.location,
            country_code=classified.country_code,
            remote_type=classified.remote_type,
            employment_type=raw.job_type,
            contract_type=classified.contract_type,
            contract_type_confidence=classified.contract_type_confidence,
            contract_evidence_kind=classified.contract_evidence_kind,
            b2b_eligible=classified.b2b_eligible,
            b2b_evidence=classified.b2b_evidence,
            residence_restriction=classified.residence_restriction,
            seniority=classified.seniority,
            role_family=classified.role_family,
            published_at=raw.published_at,
            first_seen_at=now,
            last_seen_at=now,
            status="active_unverified",
            collection_method=collection_method,
            classification_version=classified.classification_version,
            is_canonical=True,
        )
        db.add(job)
        db.flush()
        action = "inserted"

    # Replace skills/rates on update for MVP simplicity
    job.skills.clear()
    job.rates.clear()
    db.flush()

    for tech in classified.technologies:
        technology = tech_map.get(tech["canonical_name"])
        if not technology:
            continue
        job.skills.append(
            JobSkill(
                technology_id=technology.id,
                importance=tech["importance"],
                extraction_method=tech["extraction_method"],
                evidence_kind=tech["evidence_kind"],
                confidence=tech["confidence"],
                evidence_span=tech.get("evidence_span"),
            )
        )

    if classified.rate:
        r = classified.rate
        job.rates.append(
            JobRate(
                amount_min=r.get("amount_min"),
                amount_max=r.get("amount_max"),
                currency=r.get("currency"),
                unit=r.get("unit", "unknown"),
                rate_type=r.get("rate_type", "advertised"),
                evidence_text=r.get("evidence_text"),
                extraction_method=r.get("extraction_method", "rules"),
                evidence_kind=r.get("evidence_kind", "extracted"),
                confidence=r.get("confidence"),
            )
        )

    db.add(
        JobSnapshot(
            job_id=job.id,
            observed_at=now,
            status=job.status,
            title_hash=content_hash(job.title_original),
            description_hash=desc_hash,
            rate_hash=content_hash(classified.rate.get("evidence_text") if classified.rate else None),
        )
    )
    db.flush()
    return job, action


def ingest_raw_jobs(
    db: Session,
    *,
    source_id: int,
    raw_jobs: list[RawJob],
    query_id: Optional[int] = None,
    collection_method: str = "api",
) -> dict[str, Any]:
    stats = {"inserted": 0, "updated": 0, "duplicates": 0, "errors": 0}
    for raw in raw_jobs:
        try:
            _, action = upsert_raw_job(
                db,
                source_id=source_id,
                raw=raw,
                query_id=query_id,
                collection_method=collection_method,
            )
            stats[{"inserted": "inserted", "updated": "updated", "duplicate": "duplicates"}[action]] += 1
        except Exception:  # noqa: BLE001
            stats["errors"] += 1
    db.commit()
    return stats
