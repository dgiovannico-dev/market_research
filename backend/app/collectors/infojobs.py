"""InfoJobs Developer API (Spain / infojobs.net) — requires client id + secret.

InfoJobs.it closed 2025-12-31; this collector targets api.infojobs.net (ES), not Italy.
Geo affinity: ES (see COLLECTOR_GEO).

Official docs:
- Quick start: https://developer.infojobs.net/documentation/quick-start/index.xhtml
- App auth (HTTP Basic, client_id:client_secret): https://developer.infojobs.net/documentation/app-auth/index.xhtml
- Job search GET /api/1/offer: https://developer.infojobs.net/documentation/operation/offer-list-1.xhtml

Register an app on https://developer.infojobs.net/ for Client ID and Client Secret.
High-volume storage or redistribution may require a separate partner agreement
(contact gestiondatos@infojobs.net per developer terms).
"""

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
from app.core.config import get_settings
from app.secrets.resolve import credential_bundle

SEARCH_URL = "https://api.infojobs.net/api/1/offer"
MAX_PAGES = 2
DEFAULT_MAX_RESULTS = 50


def _pd_text(value: Any) -> str | None:
    if isinstance(value, dict):
        text = value.get("value")
        return str(text).strip() if text else None
    if value is not None and str(value).strip():
        return str(value).strip()
    return None


def build_search_params(
    keyword: str,
    *,
    page: int = 1,
    max_results: int = DEFAULT_MAX_RESULTS,
    country: str = "",
) -> dict[str, Any]:
    """Query params for GET /api/1/offer (keyword ``q``, pagination, optional country)."""
    params: dict[str, Any] = {
        "q": keyword,
        "page": page,
        "maxResults": max_results,
        "order": "relevancia-desc",
    }
    country = country.strip()
    if country:
        params["country"] = country
    return params


def _parse_published(value: Any) -> datetime:
    if value:
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def _parse_item(item: dict[str, Any]) -> RawJob | None:
    job_id = item.get("id")
    if not job_id:
        return None
    author = item.get("author") if isinstance(item.get("author"), dict) else {}
    company = author.get("name") if isinstance(author, dict) else None
    city = item.get("city")
    province = _pd_text(item.get("province"))
    location = ", ".join(p for p in (city, province) if p) or None
    salary_bits = [_pd_text(item.get("salaryMin")), _pd_text(item.get("salaryMax"))]
    salary_text = " - ".join(s for s in salary_bits if s) or None
    period = _pd_text(item.get("salaryPeriod"))
    if salary_text and period:
        salary_text = f"{salary_text} ({period})"
    tags: list[str] = []
    for key in ("category", "subcategory"):
        label = _pd_text(item.get(key))
        if label:
            tags.append(label)
    return RawJob(
        source_job_id=str(job_id),
        url=item.get("link") or "",
        title=item.get("title") or "Untitled",
        company=str(company) if company else None,
        description=item.get("requirementMin"),
        location=location,
        published_at=_parse_published(item.get("published") or item.get("updated")),
        salary_text=salary_text,
        tags=tags,
        job_type=_pd_text(item.get("contractType")),
        remote_hint=None,
        raw=item if isinstance(item, dict) else {},
    )


class InfoJobsCollector(BaseCollector):
    name = "InfoJobs"
    source_key = "infojobs"
    collection_mode = "search"
    base_url = SEARCH_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        if is_blank_query(query):
            return missing_query_result()
        settings = get_settings()
        creds = credential_bundle("infojobs")
        client_id = (creds.get("client_id") or "").strip()
        client_secret = (creds.get("client_secret") or "").strip()
        if not client_id or not client_secret:
            return CollectorResult(
                records=[],
                pages_scanned=0,
                errors=[
                    "INFOJOBS_CLIENT_ID and INFOJOBS_CLIENT_SECRET are required"
                ],
            )

        keyword = simplify_query_for(self, query or "")
        max_results = settings.infojobs_max_results or DEFAULT_MAX_RESULTS
        country = settings.infojobs_country.strip()
        records: list[RawJob] = []
        seen: set[str] = set()
        pages_scanned = 0
        errors: list[str] = []

        async with httpx.AsyncClient(
            timeout=45.0,
            auth=(client_id, client_secret),
            headers={"Accept": "application/json"},
        ) as client:
            for page in range(1, MAX_PAGES + 1):
                params = build_search_params(
                    keyword,
                    page=page,
                    max_results=max_results,
                    country=country,
                )
                try:
                    resp = await client.get(SEARCH_URL, params=params)
                    pages_scanned += 1
                    if resp.status_code in (401, 403):
                        return CollectorResult(
                            records=records,
                            pages_scanned=pages_scanned,
                            errors=[
                                f"InfoJobs auth failed HTTP {resp.status_code}"
                            ],
                        )
                    resp.raise_for_status()
                    payload: dict[str, Any] = resp.json() or {}
                except Exception as exc:  # noqa: BLE001
                    errors.append(str(exc))
                    break

                offers = payload.get("offers") or []
                if not isinstance(offers, list):
                    break
                for item in offers:
                    if not isinstance(item, dict):
                        continue
                    job = _parse_item(item)
                    if job is None or job.source_job_id in seen:
                        continue
                    seen.add(job.source_job_id)
                    records.append(job)

                total_pages = payload.get("totalPages")
                current_page = payload.get("currentPage") or page
                if not offers:
                    break
                if isinstance(total_pages, int) and current_page >= total_pages:
                    break
                if page >= MAX_PAGES:
                    break

        return CollectorResult(records=records, pages_scanned=pages_scanned, errors=errors)
