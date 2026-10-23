"""Landing.jobs — free public EU tech jobs JSON API (no key)."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import urlparse

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob

BASE_URL = "https://landing.jobs/api/v1/jobs"
MAX_RECORDS = 80
_COMPANY_RE = re.compile(r"/at/([^/]+)/")


class LandingJobsCollector(BaseCollector):
    name = "Landing.jobs"
    source_key = "landing_jobs"
    collection_mode = "dump"
    base_url = BASE_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        q = (query or "").strip().lower()
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=45.0, headers=headers, follow_redirects=True) as client:
                resp = await client.get(BASE_URL)
                resp.raise_for_status()
                payload = resp.json()
        except Exception as exc:  # noqa: BLE001
            return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        if not isinstance(payload, list):
            return CollectorResult(records=[], pages_scanned=1, errors=["unexpected payload"])

        records: list[RawJob] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            job_id = item.get("id")
            title = item.get("title") or "Untitled"
            url = item.get("url") or ""
            if not job_id or not url:
                continue
            if q and not _matches_query(item, q):
                continue
            if len(records) >= MAX_RECORDS:
                break
            records.append(
                RawJob(
                    source_job_id=str(job_id),
                    url=str(url),
                    title=title,
                    company=_company(url),
                    description=_description(item),
                    location=_location(item.get("locations")),
                    published_at=_published(item),
                    salary_text=_salary_text(item),
                    tags=[str(t) for t in (item.get("tags") or [])[:15] if t],
                    job_type=str(item["type"]) if item.get("type") else None,
                    remote_hint=bool(item["remote"]) if item.get("remote") is not None else None,
                    raw=_trim_raw(item),
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=[])


def _matches_query(item: dict[str, Any], q: str) -> bool:
    hay = " ".join(
        [
            str(item.get("title") or ""),
            " ".join(str(t) for t in (item.get("tags") or []) if t),
            str(item.get("role_description") or "")[:500],
        ]
    ).lower()
    return q in hay


def _company(url: str) -> str | None:
    m = _COMPANY_RE.search(urlparse(url).path or "")
    if not m:
        return None
    return m.group(1).replace("-", " ").title()


def _description(item: dict[str, Any]) -> str | None:
    for key in ("role_description", "main_requirements"):
        val = item.get(key)
        if isinstance(val, str) and val.strip():
            return val
    return None


def _location(locs: Any) -> str | None:
    if not isinstance(locs, list) or not locs:
        return None
    bits: list[str] = []
    for loc in locs[:3]:
        if not isinstance(loc, dict):
            continue
        part = ", ".join(str(x) for x in (loc.get("city"), loc.get("country_code")) if x)
        if part:
            bits.append(part)
    return "; ".join(bits) or None


def _published(item: dict[str, Any]) -> datetime:
    raw = item.get("published_at") or item.get("updated_at") or item.get("created_at")
    if raw:
        try:
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def _salary_text(item: dict[str, Any]) -> str | None:
    lo = item.get("gross_salary_low")
    hi = item.get("gross_salary_high")
    cur = item.get("currency_code") or "EUR"
    if lo is None and hi is None:
        return None
    if lo is not None and hi is not None:
        return f"{lo}-{hi} {cur}/year"
    return f"{lo or hi} {cur}/year"


def _trim_raw(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item.get("id"),
        "title": item.get("title"),
        "url": item.get("url"),
        "currency_code": item.get("currency_code"),
        "gross_salary_low": item.get("gross_salary_low"),
        "gross_salary_high": item.get("gross_salary_high"),
        "locations": item.get("locations"),
        "remote": item.get("remote"),
        "published_at": item.get("published_at"),
    }
