"""Wanted.co.kr — free public Korea jobs JSON API (no key)."""

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

BASE_URL = "https://www.wanted.co.kr/api/v4/jobs"
DETAIL_URL = "https://www.wanted.co.kr/wd/{id}"
MAX_RECORDS = 40


class WantedCollector(BaseCollector):
    name = "Wanted"
    source_key = "wanted"
    collection_mode = "search"
    base_url = BASE_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        if is_blank_query(query):
            return missing_query_result()
        q = simplify_query_for(self, query or "")
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        params = {"country": "kr", "limit": MAX_RECORDS, "query": q}
        try:
            async with httpx.AsyncClient(timeout=45.0, headers=headers, follow_redirects=True) as client:
                resp = await client.get(BASE_URL, params=params)
                resp.raise_for_status()
                payload = resp.json() or {}
        except Exception as exc:  # noqa: BLE001
            return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        data = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(data, list):
            return CollectorResult(records=[], pages_scanned=1, errors=["unexpected payload"])

        records: list[RawJob] = []
        for item in data[:MAX_RECORDS]:
            if not isinstance(item, dict):
                continue
            if item.get("status") and str(item.get("status")).lower() not in {"active", "open"}:
                continue
            job_id = item.get("id")
            title = item.get("position") or "Untitled"
            if not job_id:
                continue
            company = None
            comp = item.get("company")
            if isinstance(comp, dict):
                company = comp.get("name")
            records.append(
                RawJob(
                    source_job_id=str(job_id),
                    url=DETAIL_URL.format(id=job_id),
                    title=title,
                    company=company,
                    description=None,
                    location=_location(item.get("address")),
                    published_at=datetime.now(timezone.utc),
                    # annual_from/to are years of experience, not salary
                    salary_text=None,
                    tags=_tags(item),
                    job_type=None,
                    remote_hint=None,
                    raw=_trim_raw(item),
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=[])


def _location(addr: Any) -> str | None:
    if not isinstance(addr, dict):
        return "South Korea"
    bits = [addr.get("location"), addr.get("district"), addr.get("country")]
    joined = ", ".join(str(b) for b in bits if b)
    return joined or "South Korea"


def _tags(item: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    for t in item.get("category_tags") or []:
        if isinstance(t, dict) and t.get("title"):
            tags.append(str(t["title"]))
        elif isinstance(t, str):
            tags.append(t)
    return tags[:15]


def _trim_raw(item: dict[str, Any]) -> dict[str, Any]:
    company = item.get("company") if isinstance(item.get("company"), dict) else {}
    return {
        "id": item.get("id"),
        "position": item.get("position"),
        "status": item.get("status"),
        "address": item.get("address"),
        "company": {"id": company.get("id"), "name": company.get("name")} if company else None,
        "annual_from": item.get("annual_from"),
        "annual_to": item.get("annual_to"),
        "country_code": "KR",
    }
