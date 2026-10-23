"""Assistant compose: propose / validate / materialize (shared by HTTP + MCP)."""

from app.application.assistant.materialize import materialize_report
from app.application.assistant.propose import propose_dashboard, propose_report
from app.application.assistant.specs import DashboardSpec, ReportSpec
from app.application.assistant.validate import validate_spec

__all__ = [
    "DashboardSpec",
    "ReportSpec",
    "materialize_report",
    "propose_dashboard",
    "propose_report",
    "validate_spec",
]
