"""stdio MCP server for FMI analytics (Cursor / agents)."""

from __future__ import annotations

from typing import Any

from app.mcp import handlers


def build_mcp():
    """Build FastMCP app when SDK is installed."""
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "Package 'mcp' is required. Install backend requirements and retry: "
            "pip install mcp"
        ) from exc

    mcp = FastMCP(
        "fmi-analytics",
        instructions=(
            "Freelance Market Intelligence analytics MCP. "
            "Use get_db_metadata and get_semantic_catalog first, then propose_dashboard, "
            "propose_report, or render_demand_brief. Ground with get_observed_counts. "
            "Never invent rates. suggest_watches does not persist intents."
        ),
    )

    @mcp.tool()
    def get_db_metadata() -> dict[str, Any]:
        """Return PostgreSQL table/column/FK metadata from SQLAlchemy models."""
        return handlers.tool_get_db_metadata()

    @mcp.tool()
    def get_semantic_catalog() -> list[dict[str, Any]]:
        """Return evidence-first metric definitions and preferred API endpoints."""
        return handlers.tool_get_semantic_catalog()

    @mcp.tool()
    def list_analytics_endpoints() -> list[dict[str, Any]]:
        """List preferred FMI HTTP analytics endpoints (prefer over free SQL)."""
        return handlers.tool_list_analytics_endpoints()

    @mcp.tool()
    def run_readonly_query(
        sql: str,
        params: dict[str, Any] | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Run a single allowlisted SELECT with hard LIMIT. Rejects writes/DDL."""
        return handlers.tool_run_readonly_query(sql, params, limit=limit)

    @mcp.tool()
    def get_observed_counts(period_days: int = 90) -> dict[str, Any]:
        """Cheap observed job/source counts for grounding narratives."""
        return handlers.tool_get_observed_counts(period_days)

    @mcp.tool()
    def propose_dashboard(intent: dict[str, Any] | str) -> dict[str, Any]:
        """Propose a DashboardSpec JSON from intent hints or a user prompt string."""
        return handlers.tool_propose_dashboard(intent)

    @mcp.tool()
    def propose_report(intent: dict[str, Any] | str) -> dict[str, Any]:
        """Propose a ReportSpec JSON from intent hints or a user prompt string."""
        return handlers.tool_propose_report(intent)

    @mcp.tool()
    def render_demand_brief(
        brief_type: str,
        lens: str = "market",
        query_ids: list[int] | None = None,
        period_days: int = 90,
        country_code: str | None = None,
    ) -> dict[str, Any]:
        """Demand Compass evidence brief (rising_cooling, where_demand, adjacent,
        focus_vs_market, suggest_watches). Grounded JSON with sample_size / n=;
        suggest_watches never INSERTs SearchQuery. Optional country_code (ISO) filters
        like POST /api/v1/assistant/brief."""
        return handlers.tool_render_demand_brief(
            brief_type,
            lens=lens,
            query_ids=query_ids,
            period_days=period_days,
            country_code=country_code,
        )

    @mcp.tool()
    def validate_spec(spec: dict[str, Any]) -> dict[str, Any]:
        """Validate DashboardSpec or ReportSpec against metric catalog and policy."""
        return handlers.tool_validate_spec(spec)

    @mcp.tool()
    def materialize_report(spec: dict[str, Any]) -> dict[str, Any]:
        """Attach observed counts/sections to a ReportSpec; no invented rates."""
        return handlers.tool_materialize_report(spec)

    @mcp.tool()
    def evidence_rules() -> str:
        """Short ADR evidence rules the model must follow."""
        return handlers.tool_evidence_rules()

    @mcp.resource("fmi://evidence/rules")
    def resource_evidence_rules() -> str:
        return handlers.tool_evidence_rules()

    @mcp.resource("fmi://semantics/metrics")
    def resource_metrics() -> str:
        import json

        return json.dumps(handlers.tool_get_semantic_catalog(), indent=2)

    return mcp


def main() -> None:
    mcp = build_mcp()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
