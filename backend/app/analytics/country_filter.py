"""Parse and apply multi-country filters for analytics queries."""

from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy.sql import ColumnElement

from app.storage.models import Job


def parse_country_codes(
    raw: Optional[str | Sequence[str]] = None,
) -> list[str]:
    """Normalize CSV / list of ISO country codes. Drops empty and ``ALL``."""
    if raw is None:
        return []
    if isinstance(raw, str):
        parts = [p.strip().upper() for p in raw.split(",") if p.strip()]
    else:
        parts = [str(p).strip().upper() for p in raw if str(p).strip()]
    out: list[str] = []
    seen: set[str] = set()
    for code in parts:
        if not code or code == "ALL" or code in seen:
            continue
        seen.add(code)
        out.append(code)
    return out


def country_codes_clause(
    codes: Optional[Sequence[str]],
) -> ColumnElement[bool] | None:
    """SQLAlchemy predicate for ``Job.country_code``, or None if unscoped."""
    normalized = parse_country_codes(list(codes) if codes is not None else None)
    if not normalized:
        return None
    if len(normalized) == 1:
        return Job.country_code == normalized[0]
    return Job.country_code.in_(normalized)
