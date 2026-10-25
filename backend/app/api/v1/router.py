from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import verify_api_key
from app.api.v1.query_params import min_evidence_query, parse_lens_params
from app.application.collection.run_source import run_source as run_source_uc
from app.application.market_queries import kpis
from app.collectors.registry import CREDENTIALED_SCAFFOLDS, get_collector
from app.core.config import get_settings
from app.ingestion.import_files import import_tabular
from app.sources.insert_evidence import empty_insert_evidence, insert_evidence_by_source_id
from app.storage.db import get_db
from app.storage.models import CollectionRun, Job, SearchQuery, Source, UserProfile
from app.storage.seed import seed_reference_data

router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])


@router.get("/health")
def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": "fmi-api",
        "methodology_version": settings.methodology_version,
        "public_live": "/livez",
        "public_ready": "/readyz",
        "public_ready_alias": "/healthz",
    }


@router.post("/admin/seed")
def seed(db: Session = Depends(get_db)) -> dict[str, str]:
    seed_reference_data(db)
    return {"status": "seeded"}


@router.get("/dashboard/summary")
def dashboard_summary(
    days: int = Query(30, ge=1, le=365),
    country_code: Optional[str] = Query(
        None,
        description="ISO country code or CSV (e.g. IT,CH)",
    ),
    lens: Optional[str] = Query(
        None,
        description=(
            "Omit for all jobs (backward compatible); "
            "market | focus | compare for Demand Compass."
        ),
    ),
    query_ids: Optional[list[str]] = Query(
        None,
        description="Focus intent ids (repeated and/or comma-separated).",
    ),
    top_n: int = Query(
        100,
        ge=1,
        le=100,
        description="Max rows for top_technologies and top_countries (Mostra).",
    ),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    lens_name, qids = parse_lens_params(lens, query_ids)
    return kpis.dashboard_summary(
        db,
        days=days,
        country_code=country_code,
        lens=lens_name,
        query_ids=qids,
        top_n=top_n,
    )


@router.get("/market/jobs")
def market_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    country_code: Optional[str] = Query(
        None,
        description="ISO country code or CSV (e.g. IT,CH)",
    ),
    contract_type: Optional[str] = None,
    remote_type: Optional[str] = None,
    technology: Optional[str] = None,
    q: Optional[str] = None,
    lens: Optional[str] = Query(None, description="Omit for all jobs; market|focus|compare."),
    query_ids: Optional[list[str]] = Query(None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    lens_name, qids = parse_lens_params(lens, query_ids)
    return kpis.list_jobs(
        db,
        skip=skip,
        limit=limit,
        country_code=country_code,
        contract_type=contract_type,
        remote_type=remote_type,
        technology=technology,
        q=q,
        lens=lens_name,
        query_ids=qids,
    )


@router.get("/jobs/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    job = db.get(Job, job_id)
    if not job or not job.is_canonical:
        raise HTTPException(404, "Job not found")
    page = kpis.list_jobs(db, skip=0, limit=500)
    for item in page["items"]:
        if item["id"] == job_id:
            return item
    raise HTTPException(404, "Job not found")


@router.get("/market/trends")
def market_trends(
    days: int = Query(90, ge=7, le=365),
    min_support: int = Query(3, ge=1),
    country_code: Optional[str] = Query(
        None,
        description="ISO country code or CSV (e.g. IT,CH)",
    ),
    lens: Optional[str] = Query(None, description="Omit for all jobs; market|focus|compare."),
    query_ids: Optional[list[str]] = Query(None),
    min_evidence: Optional[str] = Query(
        None,
        description="Corpus gate: standard (default), all, or thin.",
    ),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    lens_name, qids = parse_lens_params(lens, query_ids)
    return kpis.technology_trends(
        db,
        days=days,
        min_support=min_support,
        country_code=country_code,
        lens=lens_name,
        query_ids=qids,
        min_evidence=min_evidence_query(min_evidence),
    )


@router.get("/market/technologies")
def market_technologies(
    days: int = Query(90, ge=7, le=365),
    country_code: Optional[str] = Query(
        None,
        description="ISO country code or CSV (e.g. IT,CH)",
    ),
    lens: Optional[str] = Query(None, description="Omit for all jobs; market|focus|compare."),
    query_ids: Optional[list[str]] = Query(None),
    min_evidence: Optional[str] = Query(
        None,
        description="Corpus gate: standard (default), all, or thin.",
    ),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    lens_name, qids = parse_lens_params(lens, query_ids)
    return kpis.technology_trends(
        db,
        days=days,
        min_support=1,
        country_code=country_code,
        lens=lens_name,
        query_ids=qids,
        min_evidence=min_evidence_query(min_evidence),
    )


@router.get("/market/quality")
def market_quality(
    country_code: Optional[str] = Query(
        None,
        description="ISO country code or CSV (e.g. IT,CH)",
    ),
    lens: Optional[str] = Query(None, description="Omit for all jobs; market|focus|compare."),
    query_ids: Optional[list[str]] = Query(None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    lens_name, qids = parse_lens_params(lens, query_ids)
    return kpis.data_quality_report(
        db, country_code=country_code, lens=lens_name, query_ids=qids
    )


@router.get("/sources")
def list_sources(db: Session = Depends(get_db)) -> dict[str, Any]:
    sources = db.scalars(select(Source).order_by(Source.name)).all()
    evidence = insert_evidence_by_source_id(db)
    # Demoted stubs / test fixtures stay in DB for FK safety but are not ops-facing.
    visible = [
        s
        for s in sources
        if not (s.connector_type or "").startswith("dup_")
        and (s.connector_type or "") not in {"test", "fixture", "freework", "freelancermap"}
        and not (s.name or "").startswith(("bf_src_", "dedup_empty_url_", "manual_empty", "clip-emp-"))
    ]
    return {
        "items": [
            {
                "id": s.id,
                "name": s.name,
                "connector_type": s.connector_type,
                "connector_status": s.connector_status,
                "verification_status": getattr(s, "verification_status", None),
                "catalog_id": getattr(s, "catalog_id", None),
                "category": getattr(s, "category", None),
                "access_mode": getattr(s, "access_mode", None),
                "enabled": s.enabled,
                "is_credentialed_scaffold": (s.connector_type or "") in CREDENTIALED_SCAFFOLDS,
                "coverage_notes": s.coverage_notes,
                "docs_url": s.docs_url,
                "base_url": s.base_url,
                "last_success_at": s.last_success_at.isoformat() if s.last_success_at else None,
                "last_validated_at": (
                    s.last_validated_at.isoformat()
                    if getattr(s, "last_validated_at", None)
                    else None
                ),
                "last_error": s.last_error,
                **evidence.get(s.id, empty_insert_evidence()),
            }
            for s in visible
        ]
    }


@router.post("/sources/{source_id}/run")
async def run_source(
    source_id: int,
    query: Optional[str] = None,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    source = db.get(Source, source_id)
    if not source:
        raise HTTPException(404, "Source not found")
    if source.connector_status in {"unsupported", "requires_credentials", "manual_import"}:
        raise HTTPException(
            400,
            f"Source status is {source.connector_status}. Use credentials/manual import or another connector.",
        )
    collector = get_collector(source.connector_type)
    if not collector:
        raise HTTPException(400, "No collector implementation for this source")

    result = await run_source_uc(
        db,
        source=source,
        collector=collector,
        query=query,
        collection_method="api",
    )
    if result.get("error"):
        raise HTTPException(502, result["error"])
    if result.get("skipped"):
        return {
            "status": "skipped",
            "reason": result.get("reason"),
            "verification_status": source.verification_status,
        }

    payload: dict[str, Any] = {
        "collection_run_id": result.get("run_id"),
        "status": result.get("status"),
        "records_received": result.get("records_received"),
        "inserted": result.get("inserted", 0),
        "updated": result.get("updated", 0),
        "duplicates": result.get("duplicates", 0),
        "errors": result.get("errors", 0),
        "collector_errors": result.get("collector_errors") or [],
        "verification_status": source.verification_status,
    }
    for key in ("expired_stale", "expired_unseen", "dump_complete"):
        if key in result:
            payload[key] = result[key]
    key = source.connector_type or ""
    if (
        key in CREDENTIALED_SCAFFOLDS
        and result.get("status") == "succeeded"
        and (result.get("inserted") or 0) > 0
        and source.verification_status != "ACTIVE"
    ):
        payload["next_steps"] = {
            "promote_db": (
                f"python scripts/promote_source_active.py --connector-key {key}"
            ),
            "note": (
                "Promotes Source.verification_status to ACTIVE only after insert evidence. "
                "Also update generate_source_catalog.py + regenerate catalog.json."
            ),
        }
    return payload


@router.get("/collection-runs")
def collection_runs(db: Session = Depends(get_db), limit: int = 50) -> dict[str, Any]:
    rows = db.scalars(select(CollectionRun).order_by(CollectionRun.id.desc()).limit(limit)).all()
    return {
        "items": [
            {
                "id": r.id,
                "source_id": r.source_id,
                "status": r.status,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                "records_received": r.records_received,
                "records_inserted": r.records_inserted,
                "records_updated": r.records_updated,
                "duplicates_detected": r.duplicates_detected,
                "errors_count": r.errors_count,
                "error_summary": r.error_summary,
            }
            for r in rows
        ]
    }


@router.post("/imports")
async def import_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    content = await file.read()
    if not content:
        raise HTTPException(400, "Empty file")
    return import_tabular(db, content=content, filename=file.filename or "upload.csv")


@router.get("/profile")
def get_profile(db: Session = Depends(get_db)) -> dict[str, Any]:
    profile = db.scalar(select(UserProfile).order_by(UserProfile.id).limit(1))
    if not profile:
        raise HTTPException(404, "Profile not found. Seed reference data first.")
    return {
        "id": profile.id,
        "display_name": profile.display_name,
        "years_experience": profile.years_experience,
        "residence_country": profile.residence_country,
        "languages": profile.languages,
        "remote_preference": profile.remote_preference,
        "contract_preference": profile.contract_preference,
        "min_rate_amount": profile.min_rate_amount,
        "target_rate_amount": profile.target_rate_amount,
        "rate_unit": profile.rate_unit,
        "rate_currency": profile.rate_currency,
        "skill_priority_weights": profile.skill_priority_weights,
    }


@router.get("/search-queries")
def search_queries(db: Session = Depends(get_db)) -> dict[str, Any]:
    rows = db.scalars(select(SearchQuery).order_by(SearchQuery.id)).all()
    return {
        "items": [
            {
                "id": q.id,
                "name": q.name,
                "query_text": q.query_text,
                "countries": q.countries,
                "version": q.version,
                "enabled": q.enabled,
            }
            for q in rows
        ]
    }


@router.get("/exports/jobs.csv")
def export_jobs_csv(db: Session = Depends(get_db)) -> Any:
    from fastapi.responses import StreamingResponse

    data = kpis.list_jobs(db, skip=0, limit=200)
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=[
            "id",
            "title",
            "company",
            "source",
            "country_code",
            "contract_type",
            "remote_type",
            "canonical_url",
            "published_at",
        ],
    )
    writer.writeheader()
    for item in data["items"]:
        writer.writerow({k: item.get(k) for k in writer.fieldnames})
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=fmi-jobs.csv"},
    )


@router.get("/exports/jobs.json")
def export_jobs_json(db: Session = Depends(get_db)) -> dict[str, Any]:
    data = kpis.list_jobs(db, skip=0, limit=200)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "methodology_version": get_settings().methodology_version,
        "filters": {"limit": 200},
        "record_count": data["total"],
        "disclaimer": "Observed records only; not full market size.",
        "items": data["items"],
    }
