"""Arbetsförmedlingen / JobTech JobSearch — public Swedish PES API (no key)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.collectors.base import (
    BaseCollector,
    CollectorResult,
    RawJob,
    is_blank_query,
    missing_query_result,
    simplify_query_for,
)
from app.normalization.country_codes import stamp_country_code


def _location(hit: dict[str, Any]) -> str | None:
    addr = hit.get("workplace_address") or {}
    parts = [addr.get("city") or addr.get("municipality"), addr.get("region"), addr.get("country")]
    joined = ", ".join(p for p in parts if p)
    return joined or None


def _remote_hint(hit: dict[str, Any]) -> bool | None:
    model = hit.get("workplace_model")
    if isinstance(model, dict):
        label = (model.get("label") or model.get("concept_id") or "").lower()
    else:
        label = str(model or "").lower()
    if not label:
        return None
    if "remote" in label or "distans" in label or "hemarbete" in label:
        return True
    if "on-site" in label or "på plats" in label or "pa plats" in label:
        return False
    return None


class ArbetsformedlingenCollector(BaseCollector):
    name = "Arbetsförmedlingen JobSearch"
    source_key = "arbetsformedlingen"
    collection_mode = "search"
    base_url = "https://jobsearch.api.jobtechdev.se/search"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        if is_blank_query(query):
            return missing_query_result()
        q = simplify_query_for(self, query or "")
        params: dict[str, str | int] = {"q": q, "limit": 100, "offset": 0}
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        errors: list[str] = []
        records: list[RawJob] = []

        async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
            try:
                resp = await client.get(self.base_url, params=params)
                resp.raise_for_status()
                payload = resp.json() or {}
            except Exception as exc:  # noqa: BLE001
                return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        for hit in payload.get("hits") or []:
            if not isinstance(hit, dict):
                continue
            job_id = hit.get("id")
            if job_id is None:
                continue
            title = hit.get("headline") or "Untitled"
            employer = hit.get("employer") or {}
            company = employer.get("name") or employer.get("workplace")
            desc = hit.get("description") or {}
            text = desc.get("text") if isinstance(desc, dict) else None
            pub = hit.get("publication_date") or hit.get("last_publication_date")
            published = datetime.now(timezone.utc)
            if pub:
                try:
                    published = datetime.fromisoformat(str(pub).replace("Z", "+00:00"))
                except ValueError:
                    errors.append(f"invalid date for {job_id}")
            occ = hit.get("occupation") or {}
            tags = [occ.get("label")] if isinstance(occ, dict) and occ.get("label") else []
            salary = hit.get("salary_description")
            records.append(
                RawJob(
                    source_job_id=str(job_id),
                    url=hit.get("webpage_url") or f"https://arbetsformedlingen.se/platsbanken/annonser/{job_id}",
                    title=title,
                    company=company,
                    description=text,
                    location=_location(hit),
                    published_at=published,
                    salary_text=str(salary) if salary else None,
                    tags=tags,
                    job_type=(hit.get("employment_type") or {}).get("label")
                    if isinstance(hit.get("employment_type"), dict)
                    else None,
                    remote_hint=_remote_hint(hit),
                    raw=stamp_country_code(hit, "SE"),
                )
            )

        return CollectorResult(records=records, pages_scanned=1, errors=errors)
