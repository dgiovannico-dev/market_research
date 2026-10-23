"""Credential presence for scaffolded collectors (never implies catalog ACTIVE)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.collectors.registry import COLLECTORS, CREDENTIALED_SCAFFOLDS
from app.core.config import get_settings
from app.secrets.resolve import credentials_source, has_required_credentials
from app.sources.catalog import catalog_summary
from app.storage.models import CollectionRun, Source


def has_credentials(key: str, db: Session | None = None) -> bool:
    """True when DB or env credentials allow a collect attempt. Does not mean ACTIVE."""
    if key in CREDENTIALED_SCAFFOLDS:
        return has_required_credentials(key, db=db)
    settings = get_settings()
    if key == "ashby":
        return bool(settings.ashby_orgs.strip())
    if key == "greenhouse":
        return bool(settings.greenhouse_boards.strip())
    if key == "lever":
        return bool(settings.lever_sites.strip())
    if key == "smartrecruiters":
        return bool(settings.smartrecruiters_companies.strip())
    if key == "personio":
        return bool(settings.personio_companies.strip())
    if key == "teamtailor":
        return bool(settings.teamtailor_hosts.strip())
    if key == "recruitee":
        return bool(settings.recruitee_slugs.strip())
    if key == "pinpoint":
        return bool(settings.pinpoint_subdomains.strip())
    if key == "workable":
        return bool(settings.workable_slugs.strip())
    if key == "workday":
        return bool(settings.workday_tenants.strip())
    if key == "bamboohr":
        return bool(settings.bamboohr_companies.strip())
    return True


def credentialed_connectors_status(db: Session | None = None) -> dict[str, object]:
    items = []
    for key in sorted(CREDENTIALED_SCAFFOLDS):
        ready = has_credentials(key, db=db)
        src = credentials_source(key, db=db)
        items.append(
            {
                "connector_key": key,
                "is_credentialed_scaffold": True,
                "credentials_present": ready,
                "credentials_source": src,
                "runnable_if_seeded": ready,
                "catalog_active_requires": "live_ingest_evidence",
            }
        )
    return {
        "evidence_kind": "config_observed",
        "disclaimer": (
            "Reports whether credentials are set (DB encrypted or env fallback). "
            "Does not expose secret values. ACTIVE requires a successful live run."
        ),
        "items": items,
        "docs": "docs/sources/CREDENTIALED_CONNECTORS.md",
    }


def _last_runs_by_source_id(db: Session, source_ids: list[int]) -> dict[int, CollectionRun]:
    if not source_ids:
        return {}
    latest = (
        select(
            CollectionRun.source_id.label("source_id"),
            func.max(CollectionRun.started_at).label("max_started"),
        )
        .where(CollectionRun.source_id.in_(source_ids))
        .group_by(CollectionRun.source_id)
        .subquery()
    )
    rows = db.scalars(
        select(CollectionRun).join(
            latest,
            (CollectionRun.source_id == latest.c.source_id)
            & (CollectionRun.started_at == latest.c.max_started),
        )
    ).all()
    return {run.source_id: run for run in rows}


def free_active_connectors_status(db: Session) -> list[dict[str, Any]]:
    """ACTIVE connectors that are not credentialed scaffolds, with last CollectionRun."""
    catalog_keys = {
        k
        for k in (catalog_summary().get("active_connector_keys") or [])
        if k in COLLECTORS and k not in CREDENTIALED_SCAFFOLDS
    }
    rows = list(
        db.scalars(
            select(Source).where(
                Source.verification_status == "ACTIVE",
                Source.connector_type.notin_(tuple(CREDENTIALED_SCAFFOLDS)),
            )
        ).all()
    )
    by_key = {r.connector_type: r for r in rows if r.connector_type}
    keys = sorted(catalog_keys | set(by_key))
    last_by_id = _last_runs_by_source_id(db, [by_key[k].id for k in keys if k in by_key])

    items: list[dict[str, Any]] = []
    for key in keys:
        src = by_key.get(key)
        last = last_by_id.get(src.id) if src else None
        items.append(
            {
                "connector_key": key,
                "kind": "free_active",
                "verification_status": "ACTIVE",
                "is_credentialed_scaffold": False,
                "seeded_in_db": src is not None,
                "source_id": src.id if src else None,
                "connector_status": src.connector_status if src else None,
                "enabled": bool(src.enabled) if src else False,
                "last_success_at": (
                    src.last_success_at.isoformat() if src and src.last_success_at else None
                ),
                "last_run_at": (
                    last.started_at.isoformat() if last and last.started_at else None
                ),
                "last_run_status": last.status if last else None,
                "last_run_inserted": last.records_inserted if last else None,
            }
        )
    return items


def ops_connectors_status(db: Session) -> dict[str, object]:
    """Credentialed scaffolds + free ACTIVE connectors (last run from DB)."""
    base = credentialed_connectors_status(db)
    active_free = free_active_connectors_status(db)
    return {
        **base,
        "active_free": active_free,
        "disclaimer": (
            f"{base['disclaimer']} "
            "active_free lists free ACTIVE connectors (no paid keys) with last CollectionRun."
        ),
    }
