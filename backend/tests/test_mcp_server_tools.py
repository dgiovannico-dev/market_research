from app.mcp.handlers import (
    tool_evidence_rules,
    tool_get_db_metadata,
    tool_get_semantic_catalog,
    tool_list_analytics_endpoints,
    tool_propose_dashboard,
    tool_validate_spec,
)
from app.mcp.server import build_mcp


def test_handlers_json_serializable():
    meta = tool_get_db_metadata()
    assert meta["table_count"] >= 4
    catalog = tool_get_semantic_catalog()
    assert isinstance(catalog, list) and catalog[0]["key"]
    endpoints = tool_list_analytics_endpoints()
    assert any(e["path"].endswith("/dashboard/summary") for e in endpoints)
    dash = tool_propose_dashboard("trend python 30 days")
    assert dash["period_days"] == 30
    assert tool_validate_spec(dash)["ok"] is True
    assert "observed" in tool_evidence_rules().lower()


def test_build_mcp_registers_tools():
    mcp = build_mcp()
    # FastMCP keeps tools in _tool_manager
    names = set(mcp._tool_manager._tools.keys())  # noqa: SLF001
    for expected in (
        "get_db_metadata",
        "get_semantic_catalog",
        "run_readonly_query",
        "propose_dashboard",
        "render_demand_brief",
        "validate_spec",
        "materialize_report",
    ):
        assert expected in names
