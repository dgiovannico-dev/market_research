from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics import kpis
from app.api.deps import verify_api_key
from app.collectors.registry import get_collector
from app.core.config import get_settings
from app.ingestion.import_files import import_tabular
from app.ingestion.service import ingest_raw_jobs
from app.storage.db import get_db
from app.storage.models import CollectionRun, Job, SearchQuery, Source, UserProfile
from app.storage.seed import seed_reference_data

router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "fmi-api"}


@router.post("/admin/seed")
def seed(db: Session = Depends(get_db)) -> dict[str, str]:
    seed_reference_data(db)
    return {"status": "seeded"}


@router.get("/dashboard/summary")
def dashboard_summary(
    days: int = Query(30, ge=1, le=365),
    country_code: Optional[str] = None,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return kpis.dashboard_summary(db, days=days, country_code=country_code)


@router.get("/market/jobs")
def market_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    country_code: Optional[str] = None,
    contract_type: Optional[str] = None,
    remote_type: Optional[str] = None,
    technology: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return kpis.list_jobs(
        db,
        skip=skip,
        limit=limit,
        country_code=country_code,
        contract_type=contract_type,
        remote_type=remote_type,
        technology=technology,
        q=q,
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
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return kpis.technology_trends(db, days=days, min_support=min_support)


@router.get("/market/technologies")
def market_technologies(
    days: int = Query(90, ge=7, le=365),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return kpis.technology_trends(db, days=days, min_support=1)


@router.get("/market/quality")
def market_quality(db: Session = Depends(get_db)) -> dict[str, Any]:
    return kpis.data_quality_report(db)


@router.get("/sources")
def list_sources(db: Session = Depends(get_db)) -> dict[str, Any]:
    sources = db.scalars(select(Source).order_by(Source.name)).all()
    return {
        "items": [
            {
                "id": s.id,
                "name": s.name,
                "connector_type": s.connector_type,
                "connector_status": s.connector_status,
                "enabled": s.enabled,
                "coverage_notes": s.coverage_notes,
                "last_success_at": s.last_success_at.isoformat() if s.last_success_at else None,
                "last_error": s.last_error,
            }
            for s in sources
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

    started = datetime.now(timezone.utc)
    run = CollectionRun(source_id=source.id, started_at=started, status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    result = await collector.collect(query=query)
    stats = ingest_raw_jobs(
        db,
        source_id=source.id,
        raw_jobs=result.records,
        collection_method="api",
    )
    completed = datetime.now(timezone.utc)
    run.completed_at = completed
    run.status = "partial" if result.errors else "succeeded"
    run.pages_scanned = result.pages_scanned
    run.records_received = len(result.records)
    run.records_inserted = stats["inserted"]
    run.records_updated = stats["updated"]
    run.duplicates_detected = stats["duplicates"]
    run.errors_count = stats["errors"] + len(result.errors)
    run.error_summary = "; ".join(result.errors)[:2000] if result.errors else None
    run.duration_seconds = (completed - started).total_seconds()
    source.last_success_at = completed
    source.last_error = run.error_summary
    if run.error_summary:
        source.last_error_at = completed
    db.commit()
    return {
        "collection_run_id": run.id,
        "status": run.status,
        "records_received": run.records_received,
        **stats,
        "collector_errors": result.errors,
    }


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
