from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import verify_api_key
from app.llm.classify_jobs import run_llm_classification
from app.llm.evaluation import evaluate_rules_consistency
from app.llm.provider import get_llm_provider
from app.reports.weekly import build_weekly_report
from app.scheduler.runner import evaluate_alerts, scheduler_tick
from app.storage.db import get_db
from app.storage.models import AlertRule

router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])


@router.get("/reports/weekly")
async def weekly_report(db: Session = Depends(get_db)) -> dict[str, Any]:
    return await build_weekly_report(db)


@router.post("/reports/generate")
async def generate_report(db: Session = Depends(get_db)) -> dict[str, Any]:
    return await build_weekly_report(db)


@router.post("/llm/classification/run")
async def llm_classification_run(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return await run_llm_classification(db, limit=limit)


@router.get("/llm/status")
async def llm_status_ops() -> dict[str, Any]:
    from app.core.config import get_settings

    settings = get_settings()
    provider = get_llm_provider()
    health = await provider.health()
    return {
        "classification_mode": settings.classification_mode,
        "configured_provider": settings.llm_provider,
        **health,
    }


@router.post("/llm/evaluation/run")
def llm_evaluation_run(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return evaluate_rules_consistency(db, limit=limit)


@router.post("/scheduler/run")
async def scheduler_run() -> dict[str, Any]:
    return await scheduler_tick()


@router.get("/alerts")
def list_alerts(db: Session = Depends(get_db)) -> dict[str, Any]:
    rows = db.scalars(select(AlertRule).order_by(AlertRule.id)).all()
    return {
        "items": [
            {
                "id": r.id,
                "name": r.name,
                "rule_type": r.rule_type,
                "configuration": r.configuration,
                "enabled": r.enabled,
                "last_triggered_at": r.last_triggered_at.isoformat() if r.last_triggered_at else None,
                "last_evidence": r.last_evidence,
            }
            for r in rows
        ]
    }


@router.post("/alerts/evaluate")
def alerts_evaluate() -> dict[str, Any]:
    return {"fired": evaluate_alerts()}
