"""Sync job_certifications from rules extract."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.storage.models import Certification, Job, JobCertification

# Slugs removed/merged in taxonomy → keep one canonical id in DB.
_SLUG_MERGES: dict[str, str] = {
    "scrum-csm": "csm",
    "aws-networking-specialty": "aws-advanced-networking",
}


def _merge_obsolete_slugs(db: Session, by_slug: dict[str, Certification]) -> None:
    """Re-point job links from obsolete slugs onto canonical rows, then delete obsolete."""
    from sqlalchemy import delete, update

    for obsolete_slug, keep_slug in _SLUG_MERGES.items():
        obsolete = by_slug.get(obsolete_slug)
        keep = by_slug.get(keep_slug)
        if not obsolete or not keep or obsolete.id == keep.id:
            continue
        keep_keys = {
            (e.job_id, e.importance)
            for e in db.scalars(
                select(JobCertification).where(JobCertification.certification_id == keep.id)
            ).all()
        }
        obsolete_links = list(
            db.scalars(
                select(JobCertification).where(
                    JobCertification.certification_id == obsolete.id
                )
            ).all()
        )
        drop_ids: list[int] = []
        move_ids: list[int] = []
        for link in obsolete_links:
            key = (link.job_id, link.importance)
            if key in keep_keys:
                drop_ids.append(link.id)
            else:
                move_ids.append(link.id)
                keep_keys.add(key)
        if drop_ids:
            db.execute(delete(JobCertification).where(JobCertification.id.in_(drop_ids)))
        if move_ids:
            db.execute(
                update(JobCertification)
                .where(JobCertification.id.in_(move_ids))
                .values(certification_id=keep.id)
            )
        db.execute(delete(Certification).where(Certification.id == obsolete.id))
        by_slug.pop(obsolete_slug, None)
        db.flush()


def ensure_certifications(db: Session) -> dict[str, Certification]:
    from app.classification.certs import load_cert_taxonomy

    by_slug: dict[str, Certification] = {
        c.slug: c for c in db.scalars(select(Certification)).all()
    }
    for entry in load_cert_taxonomy():
        slug = str(entry.get("slug") or "").strip()
        if not slug:
            continue
        display = str(entry.get("display_name") or slug)
        aliases = list(entry.get("aliases") or [])
        existing = by_slug.get(slug)
        if existing:
            # Keep DB row in sync with taxonomy (aliases / display can change).
            if existing.display_name != display or list(existing.aliases or []) != aliases:
                existing.display_name = display
                existing.aliases = aliases
            continue
        row = Certification(
            slug=slug,
            display_name=display,
            aliases=aliases,
        )
        db.add(row)
        db.flush()
        by_slug[slug] = row
    _merge_obsolete_slugs(db, by_slug)
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
