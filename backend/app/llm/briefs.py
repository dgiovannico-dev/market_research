"""Compatibility shim — prefer ``app.application.briefs``."""

from app.application.briefs import (
    BRIEF_TYPES,
    MIN_SAMPLE,
    THIN_SAMPLE,
    adjacent,
    focus_vs_market,
    render_brief,
    rising_cooling,
    suggest_watches,
    where_demand,
)

__all__ = [
    "BRIEF_TYPES",
    "MIN_SAMPLE",
    "THIN_SAMPLE",
    "adjacent",
    "focus_vs_market",
    "render_brief",
    "rising_cooling",
    "suggest_watches",
    "where_demand",
]
