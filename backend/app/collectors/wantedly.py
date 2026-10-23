"""Wantedly — free public Japan projects/jobs JSON (no key)."""

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

BASE_URL = "https://www.wantedly.com/api/v1/projects"
DETAIL_URL = "https://www.wantedly.com/projects/{id}"
MAX_RECORDS = 40


class WantedlyCollector(BaseCollector):
    name = "Wantedly"
    source_key = "wantedly"
    collection_mode = "search"
    base_url = BASE_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        if is_blank_query(query):
            return missing_query_result()
        q = simplify_query_for(self, query or "")
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        params = {"q": q, "page": 1}
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
            job_id = item.get("id")
            title = item.get("title") or "Untitled"
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
                    description=item.get("description") if isinstance(item.get("description"), str) else None,
                    location=item.get("location") or "Japan",
                    published_at=_published(item),
                    salary_text=None,
                    tags=_tags(item),
                    job_type=item.get("looking_for") if isinstance(item.get("looking_for"), str) else None,
                    remote_hint=None,
                    raw=_trim_raw(item),
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=[])


def _published(item: dict[str, Any]) -> datetime:
    raw = item.get("published_at")
    if raw:
        try:
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def _tags(item: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    raw = item.get("tags")
    if isinstance(raw, list):
        for t in raw[:12]:
            if isinstance(t, str):
                tags.append(t)
            elif isinstance(t, dict) and t.get("name"):
                tags.append(str(t["name"]))
    if item.get("looking_for"):
        tags.append(str(item["looking_for"]))
    return tags[:15]


def _trim_raw(item: dict[str, Any]) -> dict[str, Any]:
    company = item.get("company") if isinstance(item.get("company"), dict) else {}
    return {
        "id": item.get("id"),
        "title": item.get("title"),
        "published_at": item.get("published_at"),
        "location": item.get("location"),
        "looking_for": item.get("looking_for"),
        "company": {"id": company.get("id"), "name": company.get("name")} if company else None,
        "country_code": "JP",
    }
