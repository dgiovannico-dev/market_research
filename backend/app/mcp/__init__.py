"""MCP analytics: schema metadata + semantic specs for LLM dashboards/reports."""

from app.mcp.semantics import get_semantic_catalog
from app.mcp.specs import DashboardSpec, ReportSpec

__all__ = ["DashboardSpec", "ReportSpec", "get_semantic_catalog"]
