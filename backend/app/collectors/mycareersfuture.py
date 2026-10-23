"""MyCareersFuture Singapore — free public jobs API (no key)."""

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

BASE_URL = "https://api.mycareersfuture.gov.sg/v2/jobs"
MAX_RECORDS = 50


class MyCareersFutureCollector(BaseCollector):
    name = "MyCareersFuture"
    source_key = "mycareersfuture"
    collection_mode = "search"
    base_url = BASE_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        if is_blank_query(query):
            return missing_query_result()
        q = simplify_query_for(self, query or "")
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        params = {"limit": MAX_RECORDS, "search": q}
        try:
            async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
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
            uid = item.get("uuid")
            title = item.get("title") or "Untitled"
            if not uid:
                continue
            url = f"https://www.mycareersfuture.gov.sg/job/{uid}"
            company = None
            pc = item.get("postedCompany")
            if isinstance(pc, dict):
                company = pc.get("name")
            published = _published(item)
            salary_text = _salary_text(item.get("salary"))
            tags = _tags(item)
            job_type = _employment_type(item)
            records.append(
                RawJob(
                    source_job_id=str(uid),
                    url=url,
                    title=title,
                    company=company,
                    description=item.get("description"),
                    location=_location(item.get("address")),
                    published_at=published,
                    salary_text=salary_text,
                    tags=tags,
                    job_type=job_type,
                    remote_hint=None,
                    raw=_trim_raw(item),
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=[])


def _published(item: dict[str, Any]) -> datetime:
    meta = item.get("metadata") or {}
    raw = meta.get("createdAt") or meta.get("updatedAt") if isinstance(meta, dict) else None
    if raw:
        try:
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def _location(addr: Any) -> str | None:
    if not isinstance(addr, dict):
        return "Singapore"
    bits = [
        addr.get("building"),
        addr.get("street"),
        addr.get("postalCode"),
        addr.get("overseasCountry"),
    ]
    joined = ", ".join(str(b) for b in bits if b)
    return joined or "Singapore"


def _salary_text(salary: Any) -> str | None:
    if not isinstance(salary, dict):
        return None
    lo = salary.get("minimum")
    hi = salary.get("maximum")
    if lo is None and hi is None:
        return None
    stype = salary.get("type") or {}
    period = stype.get("salaryType") if isinstance(stype, dict) else None
    # SGD is the market currency for this government board; values are posted amounts
    return f"{lo or '?'}-{hi or '?'} SGD/{period or 'period'}"


def _tags(item: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    for skill in (item.get("skills") or [])[:12]:
        if isinstance(skill, dict) and skill.get("skill"):
            tags.append(str(skill["skill"]))
    for pl in item.get("positionLevels") or []:
        if isinstance(pl, dict) and pl.get("position"):
            tags.append(str(pl["position"]))
    return tags[:20]


def _employment_type(item: dict[str, Any]) -> str | None:
    types = item.get("employmentTypes") or []
    labels = [
        str(t.get("employmentType"))
        for t in types
        if isinstance(t, dict) and t.get("employmentType")
    ]
    return ", ".join(labels) or None


def _trim_raw(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "uuid": item.get("uuid"),
        "title": item.get("title"),
        "salary": item.get("salary"),
        "metadata": item.get("metadata"),
        "postedCompany": {"name": (item.get("postedCompany") or {}).get("name")}
        if isinstance(item.get("postedCompany"), dict)
        else None,
        "country_code": "SG",
    }
