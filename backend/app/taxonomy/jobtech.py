"""JobTech Taxonomy autocomplete (Sweden) — free public API, no key."""

from __future__ import annotations

from typing import Any

import httpx

JOBTECH_AUTOCOMPLETE_URL = (
    "https://taxonomy.api.jobtechdev.se/v1/taxonomy/suggesters/autocomplete"
)
# Map FMI-facing types to JobTech suggester types
TYPE_MAP = {
    "skill": "skill",
    "occupation": "occupation-name",
}


async def search_jobtech(
    query: str,
    *,
    type_: str = "skill",
    limit: int = 10,
) -> dict[str, Any]:
    q = (query or "").strip()
    if not q:
        return {
            "evidence_kind": "taxonomy_reference",
            "provider": "jobtech",
            "query": q,
            "items": [],
            "error": "empty_query",
        }
    jt_type = TYPE_MAP.get(type_, "skill")
    limit = max(1, min(int(limit), 25))
    headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
    params = {"query-string": q, "type": jt_type}
    try:
        async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
            resp = await client.get(JOBTECH_AUTOCOMPLETE_URL, params=params)
            resp.raise_for_status()
            payload = resp.json() or []
    except Exception as exc:  # noqa: BLE001
        return {
            "evidence_kind": "taxonomy_reference",
            "provider": "jobtech",
            "query": q,
            "type": type_,
            "items": [],
            "error": str(exc),
        }

    if not isinstance(payload, list):
        payload = []
    items: list[dict[str, Any]] = []
    for row in payload[:limit]:
        if not isinstance(row, dict):
            continue
        concept_id = row.get("taxonomy/id")
        items.append(
            {
                "title": row.get("taxonomy/preferred-label"),
                "uri": (
                    f"https://taxonomy.api.jobtechdev.se/v1/taxonomy/main/concepts/{concept_id}"
                    if concept_id
                    else None
                ),
                "code": concept_id,
                "class_name": row.get("taxonomy/type"),
                "alt_labels": row.get("taxonomy/alternative-labels") or [],
            }
        )
    return {
        "evidence_kind": "taxonomy_reference",
        "provider": "jobtech",
        "docs": "https://taxonomy.api.jobtechdev.se/",
        "query": q,
        "type": type_,
        "total": len(payload),
        "items": items,
        "disclaimer": (
            "JobTech labels are Swedish labour taxonomy reference only — "
            "not observed job counts or rates."
        ),
    }
