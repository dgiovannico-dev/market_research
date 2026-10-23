"""Eurostat dissemination API — free public JSON-stat (reference series only)."""

from __future__ import annotations

from typing import Any

import httpx

EUROSTAT_DATA_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset}"
)
# Allowlisted datasets only — avoid arbitrary pull of huge cubes
ALLOWED_DATASETS = frozenset(
    {
        "earn_ses_hourly",  # Structure of earnings — hourly
        "earn_ses18_hourly",
        "une_rt_a",  # Unemployment rates annual
        # ICT specialists in online job ads (experimental OJA) — IT/CH/LU demand mix
        "isoc_sk_oja",
        "isoc_sk_oja2",
    }
)


async def fetch_eurostat_series(
    dataset: str = "earn_ses_hourly",
    *,
    geo: str = "DE",
    time: str | None = "2022",
    limit: int = 20,
) -> dict[str, Any]:
    ds = (dataset or "").strip()
    if ds not in ALLOWED_DATASETS:
        return {
            "evidence_kind": "official_statistics_reference",
            "provider": "eurostat",
            "dataset": ds,
            "items": [],
            "error": f"dataset_not_allowlisted; allowed={sorted(ALLOWED_DATASETS)}",
        }
    geo = (geo or "DE").strip().upper()[:8]
    limit = max(1, min(int(limit), 50))
    params: dict[str, str] = {"format": "JSON", "lang": "en", "geo": geo}
    if time:
        params["time"] = str(time).strip()
    headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
    url = EUROSTAT_DATA_URL.format(dataset=ds)
    try:
        async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            payload = resp.json() or {}
    except Exception as exc:  # noqa: BLE001
        return {
            "evidence_kind": "official_statistics_reference",
            "provider": "eurostat",
            "dataset": ds,
            "geo": geo,
            "items": [],
            "error": str(exc),
        }

    label = payload.get("label") if isinstance(payload, dict) else None
    values = payload.get("value") if isinstance(payload, dict) else None
    items: list[dict[str, Any]] = []
    if isinstance(values, dict):
        for idx, (key, val) in enumerate(values.items()):
            if idx >= limit:
                break
            items.append({"index": key, "value": val})
    updated = payload.get("updated") if isinstance(payload, dict) else None
    return {
        "evidence_kind": "official_statistics_reference",
        "provider": "eurostat",
        "docs": "https://ec.europa.eu/eurostat/web/main/data/database",
        "dataset": ds,
        "label": label,
        "geo": geo,
        "time": time,
        "updated": updated,
        "total_values": len(values) if isinstance(values, dict) else 0,
        "items": items,
        "disclaimer": (
            "Eurostat official statistics for context only. "
            "Do not mix with observed job posting rates or invent day rates from these series."
        ),
    }
