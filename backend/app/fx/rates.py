"""FX helpers using Frankfurter (primary), ECB Data API, optional Open Exchange Rates."""

from __future__ import annotations

from typing import Any

import httpx

from app.core.config import get_settings


async def fetch_frankfurter_rates(base: str = "EUR", symbols: str = "USD,CHF,GBP") -> dict[str, Any]:
    url = "https://api.frankfurter.dev/v1/latest"
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        resp = await client.get(url, params={"from": base, "to": symbols})
        resp.raise_for_status()
        data = resp.json()
    return {
        "provider": "frankfurter",
        "base": data.get("base", base),
        "date": data.get("date"),
        "rates": data.get("rates") or {},
        "evidence_kind": "observed",
        "source_url": url,
    }


async def fetch_ecb_usd_eur() -> dict[str, Any]:
    """Last observation USD per EUR from ECB EXR."""
    url = "https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A"
    params = {"lastNObservations": 1, "format": "jsondata"}
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
    # Structure is verbose; surface raw series for ops + a best-effort rate
    rate = None
    try:
        datasets = data.get("dataSets") or []
        series = (datasets[0].get("series") or {}) if datasets else {}
        first = next(iter(series.values()), {})
        obs = (first.get("observations") or {}).get("0")
        if obs:
            rate = float(obs[0])
    except (StopIteration, TypeError, ValueError, IndexError, AttributeError):
        rate = None
    return {
        "provider": "ecb",
        "pair": "USD/EUR",
        "rate": rate,
        "evidence_kind": "observed",
        "source_url": url,
        "raw_header": (data.get("header") or {}),
    }


async def fetch_open_exchange_rates(base: str = "EUR", symbols: str = "USD,CHF,GBP") -> dict[str, Any]:
    """Optional OXR overlay when OPEN_EXCHANGE_RATES_APP_ID is set; never invents rates."""
    app_id = get_settings().open_exchange_rates_app_id.strip()
    if not app_id:
        return {
            "provider": "open_exchange_rates",
            "enabled": False,
            "evidence_kind": "not_configured",
            "rates": {},
            "limits": "Set OPEN_EXCHANGE_RATES_APP_ID to enable; Frankfurter/ECB remain primary.",
        }
    url = "https://openexchangerates.org/api/latest.json"
    # Free tier is USD-base; we still request and report observed base.
    params = {"app_id": app_id, "base": base, "symbols": symbols}
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            resp = await client.get(url, params=params)
            if resp.status_code in (401, 403):
                return {
                    "provider": "open_exchange_rates",
                    "enabled": True,
                    "evidence_kind": "auth_failed",
                    "rates": {},
                    "error": f"HTTP {resp.status_code}",
                }
            resp.raise_for_status()
            data = resp.json() or {}
        except Exception as exc:  # noqa: BLE001
            return {
                "provider": "open_exchange_rates",
                "enabled": True,
                "evidence_kind": "error",
                "rates": {},
                "error": str(exc),
            }
    return {
        "provider": "open_exchange_rates",
        "enabled": True,
        "base": data.get("base", base),
        "timestamp": data.get("timestamp"),
        "rates": data.get("rates") or {},
        "evidence_kind": "observed",
        "source_url": url,
    }
