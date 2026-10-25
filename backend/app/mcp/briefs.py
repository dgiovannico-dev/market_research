"""MCP wrapper for Demand Compass evidence-coach briefs."""

from __future__ import annotations

from typing import Any, Optional, Sequence

from sqlalchemy.orm import Session

from app.application.briefs import BRIEF_TYPES, render_brief

__all__ = ["BRIEF_TYPES", "render_demand_brief"]


def render_demand_brief(
    db: Session,
    *,
    brief_type: str,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    period_days: int = 90,
    country_code: Optional[str] = None,
    owned_skills: Optional[Sequence[str]] = None,
) -> dict[str, Any]:
    """Return structured brief JSON from ``render_brief`` (never invents KPIs)."""
    return render_brief(
        db,
        brief_type=brief_type,
        lens=lens,
        query_ids=query_ids,
        period_days=period_days,
        country_code=country_code,
        owned_skills=owned_skills,
    )
