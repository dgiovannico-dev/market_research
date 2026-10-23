from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import verify_api_key
from app.fx.rates import fetch_ecb_usd_eur, fetch_frankfurter_rates, fetch_open_exchange_rates
from app.application.classification import run_llm_classification
from app.bootstrap import get_container
from app.llm.evaluation import evaluate_rules_consistency
from app.llm.gold_eval import evaluate_gold_labels
from app.collectors.credentials import ops_connectors_status
from app.collectors.registry import CREDENTIALED_SCAFFOLDS
from app.ops.metrics import ops_metrics_snapshot
from app.reports.weekly import build_weekly_report
from app.scheduler.runner import evaluate_alerts, scheduler_tick
from app.storage.db import get_db
from app.storage.models import AlertRule

router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])


@router.get("/ops/metrics")
def ops_metrics(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Observed DB counters for ops dashboards (not market size)."""
    return ops_metrics_snapshot(db)


@router.get("/ops/connectors")
def ops_connectors(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Credentialed scaffolds + free ACTIVE connectors with last run (no secret values)."""
    return ops_connectors_status(db)


def _catalog_connector_key(item: dict[str, Any]) -> str:
    return str(item.get("connector_key") or item.get("key") or "").strip()


def _annotate_catalog_item(item: dict[str, Any]) -> dict[str, Any]:
    key = _catalog_connector_key(item)
    return {
        **item,
        "connector_key": key or item.get("connector_key") or item.get("key"),
        "is_credentialed_scaffold": key in CREDENTIALED_SCAFFOLDS,
    }


def _catalog_needs_credentials(item: dict[str, Any]) -> bool:
    """Scaffold keys or partner boards marked NEEDS_CREDENTIALS (Indeed/LinkedIn)."""
    if item.get("is_credentialed_scaffold"):
        return True
    return str(item.get("verification_status") or "") == "NEEDS_CREDENTIALS"


@router.get("/sources/catalog")
def sources_catalog(
    status: Optional[str] = None,
    category: Optional[str] = None,
    kind: Optional[str] = Query(
        None,
        description="free | credentialed — public vs scaffolds/partner boards",
    ),
) -> dict[str, Any]:
    catalog = get_container().source_catalog
    data = catalog.load()
    items = [_annotate_catalog_item(s) for s in (data.get("sources") or [])]
    if status:
        items = [s for s in items if s.get("verification_status") == status]
    if category:
        items = [s for s in items if s.get("category") == category]
    if kind == "free":
        items = [s for s in items if not _catalog_needs_credentials(s)]
    elif kind == "credentialed":
        items = [s for s in items if _catalog_needs_credentials(s)]
    return {"summary": catalog.summary(), "items": items}


@router.get("/sources/catalog/summary")
def sources_catalog_summary() -> dict[str, Any]:
    return get_container().source_catalog.summary()


@router.get("/fx/rates")
async def fx_rates(
    base: str = Query("EUR"),
    symbols: str = Query("USD,CHF,GBP"),
) -> dict[str, Any]:
    frankfurter = await fetch_frankfurter_rates(base=base, symbols=symbols)
    ecb = await fetch_ecb_usd_eur()
    oxr = await fetch_open_exchange_rates(base=base, symbols=symbols)
    return {"frankfurter": frankfurter, "ecb_usd_eur": ecb, "open_exchange_rates": oxr}


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
    container = get_container()
    settings = container.settings
    health = await container.llm().health()
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


@router.get("/llm/evaluation/gold")
@router.post("/llm/evaluation/gold")
def llm_evaluation_gold() -> dict[str, Any]:
    """Score rules classifier against curated gold labels (not market demand)."""
    return evaluate_gold_labels()


@router.post("/scheduler/run")
async def scheduler_run(
    force: bool = Query(False, description="Bypass UTC-day idempotency for daily crawlers"),
) -> dict[str, Any]:
    return await scheduler_tick(force=force)


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
