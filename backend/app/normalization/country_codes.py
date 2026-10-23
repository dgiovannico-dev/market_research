"""ISO country code helpers for collectors and ingest (shared, no ingestion deps)."""

from __future__ import annotations

from typing import Any

# Align with classification COUNTRY_HINTS: UK is stored as GB.
_ALIASES = {
    "uk": "GB",
    "gb": "GB",
}


def normalize_country_code(value: Any) -> str | None:
    """Normalize a country tag (e.g. gb, it) to Job.country_code ISO2.

    Returns None when the value is missing or not a usable 2-letter code.
    """
    if value is None:
        return None
    code = str(value).strip().lower()
    if not code:
        return None
    if code in _ALIASES:
        return _ALIASES[code]
    if len(code) == 2 and code.isalpha():
        return code.upper()
    return None


# Backward-compatible alias (Adzuna path segments).
normalize_adzuna_country_code = normalize_country_code


def country_code_from_adzuna_raw(raw: dict[str, Any] | None) -> str | None:
    """Read ``raw['_adzuna_country']`` when present (Adzuna-only collector tag)."""
    if not isinstance(raw, dict):
        return None
    return normalize_country_code(raw.get("_adzuna_country"))


def country_code_from_collector_raw(raw: dict[str, Any] | None) -> str | None:
    """Prefer explicit ISO tags from collectors over location text heuristics.

    Order: Adzuna path tag → ``country_code`` → ``country``.
    """
    if not isinstance(raw, dict):
        return None
    for key in ("_adzuna_country", "country_code", "country"):
        code = normalize_country_code(raw.get(key))
        if code:
            return code
    return None


def stamp_country_code(raw: dict[str, Any] | None, code: str) -> dict[str, Any]:
    """Copy ``raw`` and set ``country_code`` when ``code`` normalizes to ISO2.

    National / geo collectors use this so ingest prefers the board's home
    market over location-text heuristics.
    """
    out = dict(raw) if isinstance(raw, dict) else {}
    normalized = normalize_country_code(code)
    if normalized:
        out["country_code"] = normalized
    return out
