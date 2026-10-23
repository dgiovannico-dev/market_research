"""Instahyre — free public India job search JSON (no key)."""

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

BASE_URL = "https://www.instahyre.com/api/v1/job_search/"
MAX_RECORDS = 40


class InstahyreCollector(BaseCollector):
    name = "Instahyre"
    source_key = "instahyre"
    collection_mode = "search"
    base_url = BASE_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        if is_blank_query(query):
            return missing_query_result()
        q = simplify_query_for(self, query or "")
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        params = {"q": q, "offset": 0, "limit": MAX_RECORDS}
        try:
            async with httpx.AsyncClient(timeout=45.0, headers=headers, follow_redirects=True) as client:
                resp = await client.get(BASE_URL, params=params)
                resp.raise_for_status()
                payload = resp.json() or {}
        except Exception as exc:  # noqa: BLE001
            return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        objects = payload.get("objects") if isinstance(payload, dict) else None
        if not isinstance(objects, list):
            return CollectorResult(records=[], pages_scanned=1, errors=["unexpected payload"])

        records: list[RawJob] = []
        for item in objects[:MAX_RECORDS]:
            if not isinstance(item, dict):
                continue
            job_id = item.get("id")
            title = item.get("title") or item.get("candidate_title") or "Untitled"
            url = item.get("public_url") or ""
            if not job_id or not url:
                continue
            company = _company(item.get("employer"))
            records.append(
                RawJob(
                    source_job_id=str(job_id),
                    url=str(url),
                    title=title,
                    company=company,
                    description=None,
                    location=item.get("locations") or "India",
                    published_at=_published(item),
                    salary_text=None,
                    tags=_tags(item),
                    job_type=None,
                    remote_hint=None,
                    raw=_trim_raw(item),
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=[])


def _company(employer: Any) -> str | None:
    if isinstance(employer, dict):
        return employer.get("company_name") or employer.get("name")
    return None


def _published(item: dict[str, Any]) -> datetime:
    raw = item.get("reviewed_at")
    if raw:
        try:
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def _tags(item: dict[str, Any]) -> list[str]:
    kw = item.get("keywords")
    if isinstance(kw, list):
        return [str(k) for k in kw[:15] if k]
    if isinstance(kw, str) and kw:
        return [p.strip() for p in kw.split(",") if p.strip()][:15]
    return []


def _trim_raw(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item.get("id"),
        "title": item.get("title"),
        "public_url": item.get("public_url"),
        "locations": item.get("locations"),
        "reviewed_at": item.get("reviewed_at"),
        "country_code": "IN",
    }
