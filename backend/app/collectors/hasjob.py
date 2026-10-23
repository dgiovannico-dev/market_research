"""Hasjob.co — free public India jobs JSON board (no key)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob

BASE_URL = "https://hasjob.co/"
MAX_RECORDS = 50


class HasjobCollector(BaseCollector):
    name = "Hasjob"
    source_key = "hasjob"
    collection_mode = "dump"
    base_url = BASE_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        q = (query or "").strip().lower()
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        params = {"format": "json"}
        try:
            async with httpx.AsyncClient(timeout=45.0, headers=headers, follow_redirects=True) as client:
                resp = await client.get(BASE_URL, params=params)
                resp.raise_for_status()
                payload = resp.json() or {}
        except Exception as exc:  # noqa: BLE001
            return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        posts = _flatten_posts(payload)
        if not posts:
            return CollectorResult(records=[], pages_scanned=1, errors=["unexpected payload"])

        records: list[RawJob] = []
        for item in posts:
            if len(records) >= MAX_RECORDS:
                break
            if not isinstance(item, dict):
                continue
            title = item.get("headline") or "Untitled"
            path = item.get("url") or ""
            if not path:
                continue
            if q and q not in title.lower() and q not in str(item.get("company_name") or "").lower():
                continue
            url = path if str(path).startswith("http") else f"https://hasjob.co{path}"
            records.append(
                RawJob(
                    source_job_id=str(path).strip("/"),
                    url=url,
                    title=title,
                    company=item.get("company_name"),
                    description=None,
                    location=item.get("location") or "India",
                    published_at=_published(item),
                    salary_text=None,
                    tags=[],
                    job_type=None,
                    remote_hint=None,
                    raw=_trim_raw(item),
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=[])


def _flatten_posts(payload: dict[str, Any]) -> list[dict[str, Any]]:
    posts = payload.get("posts")
    if isinstance(posts, list) and posts:
        return [p for p in posts if isinstance(p, dict)]
    out: list[dict[str, Any]] = []
    for group in payload.get("grouped") or []:
        if isinstance(group, dict):
            for p in group.get("posts") or []:
                if isinstance(p, dict):
                    out.append(p)
    return out


def _published(item: dict[str, Any]) -> datetime:
    raw = item.get("date")
    if raw:
        try:
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def _trim_raw(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "headline": item.get("headline"),
        "company_name": item.get("company_name"),
        "location": item.get("location"),
        "url": item.get("url"),
        "date": item.get("date"),
    }
