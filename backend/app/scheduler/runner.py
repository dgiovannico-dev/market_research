from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

import structlog
from sqlalchemy import select

from app.collectors.registry import get_collector
from app.ingestion.service import ingest_raw_jobs
from app.storage.db import SessionLocal
from app.storage.models import AlertRule, CollectionRun, Source

log = structlog.get_logger()


async def run_enabled_collectors(query: str | None = None) -> list[dict[str, Any]]:
    db = SessionLocal()
    results: list[dict[str, Any]] = []
    try:
        sources = db.scalars(
            select(Source).where(Source.enabled.is_(True), Source.connector_status == "enabled")
        ).all()
        for source in sources:
            collector = get_collector(source.connector_type)
            if not collector:
                continue
            started = datetime.now(timezone.utc)
            run = CollectionRun(source_id=source.id, started_at=started, status="running")
            db.add(run)
            db.commit()
            db.refresh(run)
            try:
                collected = await collector.collect(query=query)
                stats = ingest_raw_jobs(
                    db,
                    source_id=source.id,
                    raw_jobs=collected.records,
                    collection_method="scheduled_api",
                )
                completed = datetime.now(timezone.utc)
                run.completed_at = completed
                run.status = "partial" if collected.errors else "succeeded"
                run.pages_scanned = collected.pages_scanned
                run.records_received = len(collected.records)
                run.records_inserted = stats["inserted"]
                run.records_updated = stats["updated"]
                run.duplicates_detected = stats["duplicates"]
                run.errors_count = stats["errors"] + len(collected.errors)
                run.error_summary = "; ".join(collected.errors)[:2000] if collected.errors else None
                run.duration_seconds = (completed - started).total_seconds()
                source.last_success_at = completed
                if run.error_summary:
                    source.last_error = run.error_summary
                    source.last_error_at = completed
                db.commit()
                results.append({"source": source.name, "run_id": run.id, **stats})
            except Exception as exc:  # noqa: BLE001
                db.rollback()
                source.last_error = str(exc)
                source.last_error_at = datetime.now(timezone.utc)
                db.commit()
                log.error("collector_failed", source=source.name, error=str(exc))
                results.append({"source": source.name, "error": str(exc)})
    finally:
        db.close()
    return results


def evaluate_alerts() -> list[dict[str, Any]]:
    """Evaluate simple threshold alerts against latest dashboard KPIs."""
    from app.analytics import kpis

    db = SessionLocal()
    fired: list[dict[str, Any]] = []
    try:
        summary = kpis.dashboard_summary(db, days=30)
        trends = kpis.technology_trends(db, days=60, min_support=2)
        rules = db.scalars(select(AlertRule).where(AlertRule.enabled.is_(True))).all()
        if not rules:
            # seed a default growth alert if none
            default = AlertRule(
                name="Tech growth observed",
                rule_type="technology_growth",
                configuration={"min_growth_pct": 50, "min_support": 3},
                enabled=True,
            )
            db.add(default)
            db.commit()
            rules = [default]

        for rule in rules:
            if rule.rule_type == "technology_growth":
                min_growth = float(rule.configuration.get("min_growth_pct", 50))
                hits = [
                    t
                    for t in trends["items"]
                    if t.get("status") == "ok" and (t.get("growth_pct") or 0) >= min_growth
                ]
                if hits:
                    evidence = ", ".join(
                        f"{h['technology']}={h['growth_pct']}%" for h in hits[:5]
                    )
                    rule.last_triggered_at = datetime.now(timezone.utc)
                    rule.last_evidence = evidence
                    db.commit()
                    fired.append({"rule": rule.name, "evidence": evidence, "hits": hits[:5]})
            elif rule.rule_type == "low_quality":
                # placeholder using unique jobs == 0
                unique = next(
                    (k["metric_value"] for k in summary["kpis"] if k["metric_name"] == "unique_jobs_observed"),
                    0,
                )
                if unique == 0:
                    rule.last_triggered_at = datetime.now(timezone.utc)
                    rule.last_evidence = "No observed jobs in period"
                    db.commit()
                    fired.append({"rule": rule.name, "evidence": rule.last_evidence})
    finally:
        db.close()
    return fired


async def scheduler_tick() -> dict[str, Any]:
    collections = await run_enabled_collectors()
    alerts = evaluate_alerts()
    return {
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "collections": collections,
        "alerts_fired": alerts,
    }


def start_background_scheduler(interval_seconds: int = 3600) -> asyncio.Task:
    async def _loop() -> None:
        while True:
            try:
                result = await scheduler_tick()
                log.info("scheduler_tick", **{"collections": len(result["collections"])})
            except Exception as exc:  # noqa: BLE001
                log.error("scheduler_tick_failed", error=str(exc))
            await asyncio.sleep(interval_seconds)

    return asyncio.create_task(_loop())
