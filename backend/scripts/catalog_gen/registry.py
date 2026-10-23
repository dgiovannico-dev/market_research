"""Mutable source list and the shared `add()` helper."""

from __future__ import annotations

# Status after 2026-10-20 probes / docs review. ACTIVE only if connector tested with live data.
# Do not invent credentials success.

SOURCES: list[dict] = []


def add(
    cid: int,
    name: str,
    category: str,
    url: str,
    *,
    status: str,
    access: str,
    docs_url: str | None = None,
    notes: str = "",
    connector_key: str | None = None,
    duplicate_of: int | None = None,
) -> None:
    SOURCES.append(
        {
            "catalog_id": cid,
            "name": name,
            "category": category,
            "official_url": url,
            "docs_url": docs_url or url,
            "verification_status": status,
            "access_mode": access,
            "connector_key": connector_key,
            "duplicate_of": duplicate_of,
            "notes": notes,
            "verified_at": "2026-10-20" if status in {"ACTIVE", "VALIDATED", "NEEDS_CREDENTIALS", "REJECTED", "BLOCKED"} else None,
        }
    )


def reset() -> None:
    """Clear SOURCES (tests / re-runs in the same process)."""
    SOURCES.clear()
