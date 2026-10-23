"""Demand Compass evidence-coach briefs (SPEC-research-intents §4 J5 / §10).

Public entry: ``render_brief``. Handlers live in ``brief_handlers``; shared
constants/helpers in ``brief_support``. ``suggest_watches`` never persists.
"""

from __future__ import annotations

from typing import Any, Optional, Sequence

from sqlalchemy.orm import Session

from app.application.briefs.handlers import (
    adjacent,
    focus_vs_market,
    rising_cooling,
    suggest_watches,
    where_demand,
)
from app.application.briefs.support import (
    BRIEF_TYPES,
    DEFAULT_LENS,
    MIN_SAMPLE,
    THIN_SAMPLE,
    base_payload,
)

__all__ = [
    "BRIEF_TYPES",
    "MIN_SAMPLE",
    "THIN_SAMPLE",
    "render_brief",
    "rising_cooling",
    "where_demand",
    "adjacent",
    "focus_vs_market",
    "suggest_watches",
]

_HANDLERS = {
    "rising_cooling": rising_cooling,
    "where_demand": where_demand,
    "adjacent": adjacent,
    "focus_vs_market": focus_vs_market,
    "suggest_watches": suggest_watches,
}


def render_brief(
    db: Session,
    *,
    brief_type: str,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    period_days: int = 90,
    country_code: Optional[str] = None,
) -> dict[str, Any]:
    if brief_type not in BRIEF_TYPES:
        return base_payload(
            brief_type=brief_type,
            lens=lens or DEFAULT_LENS,
            sample_size=0,
            evidence=[],
            narrative=f"Unknown brief_type={brief_type!r}.",
            limits="Valid: " + ", ".join(sorted(BRIEF_TYPES)),
            status="refused",
        )
    resolved = lens or ("compare" if brief_type == "focus_vs_market" else DEFAULT_LENS)
    if resolved not in ("market", "focus", "compare"):
        return base_payload(
            brief_type=brief_type,
            lens=resolved,
            sample_size=0,
            evidence=[],
            narrative=f"Unknown lens={resolved!r}.",
            limits="Valid lenses: market, focus, compare",
            status="refused",
        )
    return _HANDLERS[brief_type](
        db,
        lens=resolved,
        query_ids=query_ids,
        period_days=period_days,
        country_code=country_code,
    )
