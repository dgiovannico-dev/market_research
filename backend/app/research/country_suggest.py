"""Suggest CountryFilter ISO codes from research intents (never auto-apply)."""

from __future__ import annotations

from typing import Any, Sequence


def suggested_countries_from_intents(
    intents: Sequence[Any],
    *,
    enabled_only: bool = True,
) -> list[str]:
    """Unique ISO2-ish codes from intent.countries (skip ALL / blanks)."""
    seen: set[str] = set()
    out: list[str] = []
    for intent in intents:
        if enabled_only and not getattr(intent, "enabled", True):
            continue
        for raw in getattr(intent, "countries", None) or []:
            code = str(raw).strip().upper()
            if not code or code == "ALL" or code in seen:
                continue
            seen.add(code)
            out.append(code)
    return out


def missing_suggested_countries(
    current: Sequence[str],
    suggested: Sequence[str],
) -> list[str]:
    have = {str(c).strip().upper() for c in current if str(c).strip()}
    return [c for c in suggested if c not in have]
