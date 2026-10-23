"""In-process MCP tool handlers (also used by tests)."""

from __future__ import annotations

from typing import Any

from app.application.assistant import (
    materialize_report,
    propose_dashboard,
    propose_report,
    validate_spec,
)
from app.application.assistant.observed import get_observed_counts
from app.application.assistant.semantics import get_semantic_catalog
from app.application.assistant.specs import ReportSpec
from app.application.briefs import render_brief as render_demand_brief
from app.mcp.endpoints import list_analytics_endpoints
from app.mcp.metadata import get_db_metadata
from app.mcp.query import run_readonly_query


def _session_factory():
    """Readonly-preferring sessionmaker from the composition root (patchable in tests)."""
    from app.bootstrap import get_container

    return get_container().readonly_session_factory


def tool_get_db_metadata() -> dict[str, Any]:
    return get_db_metadata()


def tool_get_semantic_catalog() -> list[dict[str, Any]]:
    return [m.model_dump() for m in get_semantic_catalog()]


def tool_list_analytics_endpoints() -> list[dict[str, Any]]:
    return list_analytics_endpoints()


def tool_run_readonly_query(
    sql: str,
    params: dict[str, Any] | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    db = _session_factory()()
    try:
        result = run_readonly_query(db, sql, params, limit=limit)
        return {
            "ok": result.ok,
            "error": result.error,
            "columns": result.columns,
            "rows": result.rows,
            "row_count": result.row_count,
            "truncated": result.truncated,
            "tables": result.tables,
        }
    finally:
        db.close()


def tool_get_observed_counts(period_days: int = 90) -> dict[str, Any]:
    db = _session_factory()()
    try:
        return get_observed_counts(db, period_days)
    finally:
        db.close()


def tool_propose_dashboard(intent: dict[str, Any] | str) -> dict[str, Any]:
    return propose_dashboard(intent).model_dump()


def tool_propose_report(intent: dict[str, Any] | str) -> dict[str, Any]:
    return propose_report(intent).model_dump()


def tool_render_demand_brief(
    brief_type: str,
    lens: str = "market",
    query_ids: list[int] | None = None,
    period_days: int = 90,
    country_code: str | None = None,
) -> dict[str, Any]:
    """Demand Compass brief; ``suggest_watches`` returns candidates only (no INSERT)."""
    db = _session_factory()()
    try:
        return render_demand_brief(
            db,
            brief_type=brief_type,
            lens=lens,
            query_ids=query_ids,
            period_days=period_days,
            country_code=country_code,
        )
    finally:
        db.close()


def tool_validate_spec(spec: dict[str, Any]) -> dict[str, Any]:
    return validate_spec(spec).to_dict()


def tool_materialize_report(spec: dict[str, Any]) -> dict[str, Any]:
    db = _session_factory()()
    try:
        return materialize_report(db, ReportSpec.model_validate(spec))
    finally:
        db.close()


EVIDENCE_RULES = """
FMI evidence rules for agents:
- Counts mean observed records in this database, never total market size.
- Missing rates are NULL / undeclared — never invent medians or coerce to zero.
- Prefer list_analytics_endpoints over free SQL.
- Use render_demand_brief for Demand Compass briefs; disclose n= from sample_size.
- suggest_watches returns candidates only — persist via POST /research/watches/accept.
- Only ACTIVE/enabled sources ingest jobs; catalog size ≠ coverage.
- Do not scrape or write via MCP tools.
- Job.evidence_tier is thin|standard; thin = capped/snapshot sources (weaker evidence).
- Default min_evidence=standard excludes thin from skills/rates/trends/brief sample sizes.
- GET /api/v1/market/quality keeps thin rows (no min_evidence gate); use by_source.pct_thin.
- closed_stale soft-expired jobs leave the DSS corpus (base_job_query excludes them).
- For thin share in a lens, prefer GET /api/v1/market/quality over inferring from KPIs.
""".strip()


def tool_evidence_rules() -> str:
    return EVIDENCE_RULES
