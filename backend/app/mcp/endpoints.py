"""Preferred analytics HTTP endpoints for MCP agents."""

from __future__ import annotations

from typing import Any


def list_analytics_endpoints() -> list[dict[str, Any]]:
    return [
        {
            "method": "GET",
            "path": "/api/v1/dashboard/summary",
            "purpose": "KPI summary with definition/sample_size/limits",
        },
        {
            "method": "GET",
            "path": "/api/v1/market/rates",
            "purpose": (
                "Rate distribution (NULL excluded); default min_evidence=standard "
                "excludes Job.evidence_tier=thin"
            ),
        },
        {
            "method": "GET",
            "path": "/api/v1/market/countries",
            "purpose": "Country breakdown",
        },
        {
            "method": "GET",
            "path": "/api/v1/market/skills/cooccurrence",
            "purpose": (
                "Skill co-occurrence; default min_evidence=standard excludes thin tier"
            ),
        },
        {
            "method": "GET",
            "path": "/api/v1/market/trends",
            "purpose": (
                "Technology trends; default min_evidence=standard excludes thin tier"
            ),
        },
        {
            "method": "GET",
            "path": "/api/v1/market/quality",
            "purpose": (
                "Data quality / coverage (includes thin jobs; by_source.pct_thin; "
                "no min_evidence gate)"
            ),
        },
        {
            "method": "GET",
            "path": "/api/v1/sources",
            "purpose": "Source registry / runnable connectors",
        },
        {
            "method": "GET",
            "path": "/api/v1/sources/catalog/summary",
            "purpose": "Global catalog status counts",
        },
        {
            "method": "GET",
            "path": "/api/v1/reports/weekly",
            "purpose": "Weekly report JSON",
        },
        {
            "method": "GET",
            "path": "/api/v1/profile/skill-gaps",
            "purpose": "Profile skill gaps (guided)",
        },
        {
            "method": "POST",
            "path": "/api/v1/assistant/brief",
            "purpose": (
                "Demand Compass evidence brief (same contract as MCP render_demand_brief); "
                "min_evidence=standard excludes thin from sample_size"
            ),
        },
        {
            "method": "POST",
            "path": "/api/v1/research/watches/accept",
            "purpose": "Persist suggest_watches candidates (MCP never INSERTs SearchQuery)",
        },
    ]
