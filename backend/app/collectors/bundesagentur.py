"""Bundesagentur für Arbeit Jobsuche API — requires BUNDESAGENTUR_API_KEY (X-API-Key)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from urllib.parse import quote

import httpx

from app.collectors.base import (
    BaseCollector,
    CollectorResult,
    RawJob,
    is_blank_query,
    missing_query_result,
    simplify_query_for,
)
from app.core.config import get_settings
from app.secrets.resolve import credential_bundle


class BundesagenturCollector(BaseCollector):
    name = "Bundesagentur für Arbeit"
    source_key = "bundesagentur"
    collection_mode = "search"
    base_url = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        if is_blank_query(query):
            return missing_query_result()
        settings = get_settings()
        api_key = (credential_bundle("bundesagentur").get("api_key") or "").strip()
        if not api_key:
            return CollectorResult(
                records=[],
                pages_scanned=0,
                errors=["BUNDESAGENTUR_API_KEY is required"],
            )

        was = simplify_query_for(self, query or "")
        wo = settings.bundesagentur_location.strip() or "Berlin"
        params = {
            "was": was,
            "wo": wo,
            "page": 1,
            "size": 50,
        }
        headers = {
            "X-API-Key": api_key,
            "Accept": "application/json",
            "User-Agent": "FMI-MarketIntel/1.0",
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            try:
                resp = await client.get(self.base_url, params=params, headers=headers)
                if resp.status_code in (401, 403):
                    return CollectorResult(
                        records=[],
                        pages_scanned=1,
                        errors=[f"Bundesagentur auth failed HTTP {resp.status_code}"],
                    )
                resp.raise_for_status()
                payload = resp.json() or {}
            except Exception as exc:  # noqa: BLE001
                return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        offers = payload.get("ergebnisliste") or payload.get("stellenangebote") or []
        records: list[RawJob] = []
        for item in offers:
            refnr = item.get("referenznummer") or item.get("refnr")
            if not refnr:
                continue
            location = None
            locs = item.get("stellenlokationen") or []
            if isinstance(locs, list) and locs:
                addr = (locs[0] or {}).get("adresse") or {}
                if isinstance(addr, dict):
                    location = addr.get("ort") or addr.get("plz")
            company = item.get("firma")
            if isinstance(company, dict):
                company = company.get("name")
            published = datetime.now(timezone.utc)
            pub_raw = item.get("datumErsteVeroeffentlichung") or item.get("aenderungsdatum")
            if pub_raw:
                try:
                    published = datetime.fromisoformat(str(pub_raw).replace("Z", "+00:00"))
                except ValueError:
                    pass
            url = item.get("externeURL") or (
                f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{quote(str(refnr), safe='')}"
            )
            salary_text = None
            if item.get("festgehalt") is not None:
                salary_text = f"{item.get('festgehalt')} {item.get('verguetungsangabe') or ''}".strip()
            remote = "remote" if item.get("homeofficemoeglich") else None
            records.append(
                RawJob(
                    source_job_id=str(refnr),
                    url=url,
                    title=item.get("stellenangebotsTitel") or item.get("titel") or "Untitled",
                    company=company if isinstance(company, str) else None,
                    description=None,
                    location=location,
                    published_at=published,
                    salary_text=salary_text,
                    tags=[],
                    job_type=item.get("stellenangebotsart"),
                    remote_hint=remote,
                    raw=item if isinstance(item, dict) else {},
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=[])
