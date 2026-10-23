"""Adzuna Job Search API — requires ADZUNA_APP_ID + ADZUNA_APP_KEY."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
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

RESULTS_PER_PAGE = 50
MAX_PAGES_PER_COUNTRY = 2


def resolve_adzuna_countries(countries: str, country: str) -> list[str]:
    """Prefer ADZUNA_COUNTRIES; else ADZUNA_COUNTRY; else gb. Deduped, order preserved."""
    parts = [p.strip().lower() for p in (countries or "").split(",") if p.strip()]
    if parts:
        return list(dict.fromkeys(parts))
    fallback = (country or "gb").strip().lower() or "gb"
    return [fallback]


def _parse_item(item: dict[str, Any], country: str) -> RawJob | None:
    job_id = item.get("id")
    if job_id is None:
        return None
    created = item.get("created")
    published = None
    if created:
        try:
            published = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
        except ValueError:
            published = None
    loc = item.get("location") or {}
    location = loc.get("display_name") if isinstance(loc, dict) else None
    company = None
    company_obj = item.get("company")
    if isinstance(company_obj, dict):
        company = company_obj.get("display_name")
    salary_bits = []
    if item.get("salary_min") is not None:
        salary_bits.append(str(item.get("salary_min")))
    if item.get("salary_max") is not None:
        salary_bits.append(str(item.get("salary_max")))
    raw = dict(item) if isinstance(item, dict) else {}
    raw["_adzuna_country"] = country
    return RawJob(
        source_job_id=str(job_id),
        url=item.get("redirect_url") or item.get("adref") or "",
        title=item.get("title") or "Untitled",
        company=company,
        description=item.get("description"),
        location=location,
        published_at=published or datetime.now(timezone.utc),
        salary_text=" - ".join(salary_bits) if salary_bits else None,
        tags=[],
        job_type=item.get("contract_type") or item.get("contract_time"),
        remote_hint=None,
        raw=raw,
    )


class AdzunaCollector(BaseCollector):
    name = "Adzuna"
    source_key = "adzuna"
    collection_mode = "search"
    base_url = "https://api.adzuna.com/v1/api/jobs"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        if is_blank_query(query):
            return missing_query_result()
        settings = get_settings()
        creds = credential_bundle("adzuna")
        app_id = (creds.get("app_id") or "").strip()
        app_key = (creds.get("app_key") or "").strip()
        if not app_id or not app_key:
            return CollectorResult(
                records=[],
                pages_scanned=0,
                errors=["ADZUNA_APP_ID and ADZUNA_APP_KEY are required"],
            )

        countries = resolve_adzuna_countries(
            settings.adzuna_countries, settings.adzuna_country
        )
        what = simplify_query_for(self, query or "")
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": RESULTS_PER_PAGE,
            "what": what,
            "content-type": "application/json",
        }
        errors: list[str] = []
        seen: set[str] = set()
        records: list[RawJob] = []
        pages_scanned = 0

        async with httpx.AsyncClient(timeout=45.0) as client:
            for country in countries:
                for page in range(1, MAX_PAGES_PER_COUNTRY + 1):
                    url = f"{self.base_url}/{quote(country)}/search/{page}"
                    try:
                        resp = await client.get(url, params=params)
                        pages_scanned += 1
                        if resp.status_code in (401, 403):
                            return CollectorResult(
                                records=records,
                                pages_scanned=pages_scanned,
                                errors=[
                                    *errors,
                                    f"Adzuna auth failed HTTP {resp.status_code}",
                                ],
                            )
                        resp.raise_for_status()
                        payload = resp.json()
                    except Exception as exc:  # noqa: BLE001
                        errors.append(f"{country} p{page}: {exc}")
                        break

                    results = payload.get("results") or []
                    for item in results:
                        if not isinstance(item, dict):
                            continue
                        job = _parse_item(item, country)
                        if job is None or job.source_job_id in seen:
                            continue
                        seen.add(job.source_job_id)
                        records.append(job)

                    if len(results) < RESULTS_PER_PAGE:
                        break

        return CollectorResult(records=records, pages_scanned=pages_scanned, errors=errors)
