"""ESCO public search API (EU) — free, no API key."""

from __future__ import annotations

from typing import Any

import httpx

ESCO_SEARCH_URL = "https://ec.europa.eu/esco/api/search"
ALLOWED_TYPES = frozenset({"occupation", "skill", "concept"})


async def search_esco(
    query: str,
    *,
    type_: str = "occupation",
    language: str = "en",
    limit: int = 10,
) -> dict[str, Any]:
    q = (query or "").strip()
    if not q:
        return {
            "evidence_kind": "taxonomy_reference",
            "provider": "esco",
            "query": q,
            "items": [],
            "error": "empty_query",
        }
    kind = type_ if type_ in ALLOWED_TYPES else "occupation"
    limit = max(1, min(int(limit), 25))
    language = (language or "en")[:8]
    headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
    params = {
        "text": q,
        "language": language,
        "type": kind,
        "limit": limit,
        "full": "false",
    }
    try:
        async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
            resp = await client.get(ESCO_SEARCH_URL, params=params)
            resp.raise_for_status()
            payload = resp.json() or {}
    except Exception as exc:  # noqa: BLE001
        return {
            "evidence_kind": "taxonomy_reference",
            "provider": "esco",
            "query": q,
            "type": kind,
            "language": language,
            "items": [],
            "error": str(exc),
        }

    items: list[dict[str, Any]] = []
    for row in (payload.get("_embedded") or {}).get("results") or []:
        if not isinstance(row, dict):
            continue
        items.append(
            {
                "title": row.get("title"),
                "uri": row.get("uri"),
                "code": row.get("code"),
                "class_name": row.get("className"),
                "status": row.get("status"),
            }
        )
    return {
        "evidence_kind": "taxonomy_reference",
        "provider": "esco",
        "docs": "https://ec.europa.eu/esco/api",
        "query": q,
        "type": kind,
        "language": language,
        "total": payload.get("total"),
        "items": items,
        "disclaimer": (
            "ESCO labels are reference taxonomy only — not observed job counts or rates."
        ),
    }
