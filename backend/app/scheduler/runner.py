from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

import structlog
from sqlalchemy import select

from app.bootstrap import get_container
from app.scheduler.daily_crawlers import run_daily_crawlers
from app.storage.models import AlertRule

log = structlog.get_logger()


async def run_enabled_collectors(query: str | None = None) -> list[dict[str, Any]]:
    """Backward-compatible entry: runs budgeted daily crawlers (query ignored)."""
    del query  # product path no longer fans out a single env/default topic
    result = await run_daily_crawlers(force=True)
    return list(result.get("collections") or [])


def evaluate_alerts() -> list[dict[str, Any]]:
    """Evaluate simple threshold alerts against latest dashboard KPIs."""
    from app.analytics import kpis

    fired: list[dict[str, Any]] = []
    with get_container().session_scope() as db:
        summary = kpis.dashboard_summary(db, days=30)
        trends = kpis.technology_trends(db, days=60, min_support=2)
        rules = db.scalars(select(AlertRule).where(AlertRule.enabled.is_(True))).all()
        if not rules:
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
                unique = next(
                    (
                        k["metric_value"]
                        for k in summary["kpis"]
                        if k["metric_name"] == "unique_jobs_observed"
                    ),
                    0,
                )
                if unique == 0:
                    rule.last_triggered_at = datetime.now(timezone.utc)
                    rule.last_evidence = "No observed jobs in period"
                    db.commit()
                    fired.append({"rule": rule.name, "evidence": rule.last_evidence})
    return fired


def _thin_scheduler_response(result: dict[str, Any], *, alerts: list[dict[str, Any]]) -> dict[str, Any]:
    """Public tick payload: counts + summary only (no full collection lists)."""
    return {
        "status": result.get("status"),
        "idempotent": result.get("idempotent"),
        "day": result.get("day"),
        "ran_at": result.get("ran_at"),
        "dump_ran": result.get("dump_ran", 0),
        "discovery_ran": result.get("discovery_ran", 0),
        "focus_ran": result.get("focus_ran", 0),
        "calls": result.get("calls", 0),
        "summary": result.get("summary"),
        "alerts_fired": alerts,
    }


async def scheduler_tick(*, force: bool = False) -> dict[str, Any]:
    result = await run_daily_crawlers(force=force)
    if result.get("status") == "skipped_idempotent":
        return _thin_scheduler_response(result, alerts=[])
    alerts = evaluate_alerts()
    return _thin_scheduler_response(result, alerts=alerts)


def start_background_scheduler(interval_seconds: int = 3600) -> asyncio.Task:
    async def _loop() -> None:
        while True:
            try:
                result = await scheduler_tick()
                log.info(
                    "scheduler_tick",
                    status=result.get("status"),
                    collections=len(result.get("collections") or []),
                    calls=result.get("calls"),
                )
            except Exception as exc:  # noqa: BLE001
                log.error("scheduler_tick_failed", error=str(exc))
            await asyncio.sleep(interval_seconds)

    return asyncio.create_task(_loop())
