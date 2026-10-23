"""Duunitori.fi — free public Finland jobentries JSON API (no key)."""

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

BASE_URL = "https://duunitori.fi/api/v1/jobentries"
DETAIL_URL = "https://duunitori.fi/tyopaikat/tyo/{slug}"
MAX_RECORDS = 50


class DuunitoriCollector(BaseCollector):
    name = "Duunitori"
    source_key = "duunitori"
    collection_mode = "search"
    base_url = BASE_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        if is_blank_query(query):
            return missing_query_result()
        q = simplify_query_for(self, query or "")
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        params = {"search": q, "page": 1}
        try:
            async with httpx.AsyncClient(timeout=45.0, headers=headers, follow_redirects=True) as client:
                resp = await client.get(BASE_URL, params=params)
                resp.raise_for_status()
                payload = resp.json() or {}
        except Exception as exc:  # noqa: BLE001
            return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        results = payload.get("results") if isinstance(payload, dict) else None
        if not isinstance(results, list):
            return CollectorResult(records=[], pages_scanned=1, errors=["unexpected payload"])

        records: list[RawJob] = []
        for item in results[:MAX_RECORDS]:
            if not isinstance(item, dict):
                continue
            slug = item.get("slug")
            title = item.get("heading") or "Untitled"
            if not slug:
                continue
            records.append(
                RawJob(
                    source_job_id=str(slug),
                    url=DETAIL_URL.format(slug=slug),
                    title=title,
                    company=item.get("company_name"),
                    description=item.get("descr") if isinstance(item.get("descr"), str) else None,
                    location=item.get("municipality_name") or "Finland",
                    published_at=_published(item),
                    salary_text=None,
                    tags=[],
                    job_type=None,
                    remote_hint=None,
                    raw=_trim_raw(item),
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=[])


def _published(item: dict[str, Any]) -> datetime:
    raw = item.get("date_posted")
    if raw:
        try:
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def _trim_raw(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "slug": item.get("slug"),
        "heading": item.get("heading"),
        "company_name": item.get("company_name"),
        "municipality_name": item.get("municipality_name"),
        "date_posted": item.get("date_posted"),
        "country_code": "FI",
    }
