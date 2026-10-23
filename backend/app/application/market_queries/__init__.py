"""CQRS-light market query facades (Wave 8).

Stable surface for HTTP/MCP drivers. SQL stays in ``app.analytics``;
callers should prefer this package over reaching into KPI internals.
"""

from app.application.market_queries.kpis import (
    dashboard_summary,
    data_quality_report,
    list_jobs,
    technology_trends,
)
from app.application.market_queries.lenses import compare_counts, resolve_job_id_subquery

__all__ = [
    "compare_counts",
    "dashboard_summary",
    "data_quality_report",
    "list_jobs",
    "resolve_job_id_subquery",
    "technology_trends",
]
