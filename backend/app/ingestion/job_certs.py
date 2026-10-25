"""Sync job_certifications from rules extract."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.storage.models import Certification, Job, JobCertification


def ensure_certifications(db: Session) -> dict[str, Certification]:
    from app.classification.certs import load_cert_taxonomy

    by_slug: dict[str, Certification] = {
        c.slug: c for c in db.scalars(select(Certification)).all()
    }
    for entry in load_cert_taxonomy():
        slug = str(entry.get("slug") or "").strip()
        if not slug:
            continue
        if slug in by_slug:
            continue
        row = Certification(
            slug=slug,
            display_name=str(entry.get("display_name") or slug),
            aliases=list(entry.get("aliases") or []),
        )
        db.add(row)
        db.flush()
        by_slug[slug] = row
    return by_slug


def sync_job_certifications(
    db: Session,
    job: Job,
    *,
    extracted: Iterable[Mapping[str, Any]],
    cert_map: Mapping[str, Certification],
) -> bool:
    desired: list[tuple[int, str]] = []
    for item in extracted:
        cert = cert_map.get(str(item.get("slug") or ""))
        if not cert:
            continue
        desired.append((cert.id, str(item.get("importance") or "mentioned")))
    desired_set = frozenset(desired)
    existing = list(
        db.scalars(select(JobCertification).where(JobCertification.job_id == job.id)).all()
    )
    existing_set = frozenset((e.certification_id, e.importance) for e in existing)
    if existing_set == desired_set:
        return False
    for e in existing:
        db.delete(e)
    db.flush()
    by_item = {str(i.get("slug")): i for i in extracted}
    for cert_id, importance in desired:
        slug = next((s for s, c in cert_map.items() if c.id == cert_id), "")
        span = (by_item.get(slug) or {}).get("evidence_span")
        db.add(
            JobCertification(
                job_id=job.id,
                certification_id=cert_id,
                importance=importance,
                extraction_method="rules",
                evidence_span=str(span)[:500] if span else None,
            )
        )
    return True
