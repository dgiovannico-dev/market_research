"""Kalibrr — free public SEA job board search JSON (no key)."""

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

BASE_URL = "https://www.kalibrr.com/api/job_board/search"
MAX_RECORDS = 50


class KalibrrCollector(BaseCollector):
    name = "Kalibrr"
    source_key = "kalibrr"
    collection_mode = "search"
    base_url = BASE_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        if is_blank_query(query):
            return missing_query_result()
        q = simplify_query_for(self, query or "")
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        params = {"limit": MAX_RECORDS, "offset": 0, "text": q}
        try:
            async with httpx.AsyncClient(timeout=45.0, headers=headers, follow_redirects=True) as client:
                resp = await client.get(BASE_URL, params=params)
                resp.raise_for_status()
                payload = resp.json() or {}
        except Exception as exc:  # noqa: BLE001
            return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        jobs = payload.get("jobs") if isinstance(payload, dict) else None
        if not isinstance(jobs, list):
            return CollectorResult(records=[], pages_scanned=1, errors=["unexpected payload"])

        records: list[RawJob] = []
        for item in jobs[:MAX_RECORDS]:
            if not isinstance(item, dict):
                continue
            job_id = item.get("id")
            title = item.get("name") or "Untitled"
            if not job_id:
                continue
            url = _detail_url(item, job_id)
            records.append(
                RawJob(
                    source_job_id=str(job_id),
                    url=url,
                    title=title,
                    company=item.get("company_name"),
                    description=item.get("description") if isinstance(item.get("description"), str) else None,
                    location=_location(item),
                    published_at=_published(item),
                    salary_text=_salary_text(item),
                    tags=_tags(item),
                    job_type=item.get("tenure") if isinstance(item.get("tenure"), str) else None,
                    remote_hint=bool(item["is_work_from_home"])
                    if item.get("is_work_from_home") is not None
                    else None,
                    raw=_trim_raw(item),
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=[])


def _detail_url(item: dict[str, Any], job_id: Any) -> str:
    company = item.get("company") if isinstance(item.get("company"), dict) else {}
    code = company.get("code") or (item.get("company_info") or {}).get("code")
    slug = item.get("slug") or "job"
    if code:
        return f"https://www.kalibrr.com/c/{code}/jobs/{job_id}/{slug}"
    return f"https://www.kalibrr.com/jobs/{job_id}/{slug}"


def _location(item: dict[str, Any]) -> str | None:
    gl = item.get("google_location") or {}
    comps = gl.get("address_components") if isinstance(gl, dict) else None
    if isinstance(comps, dict):
        bits = [comps.get("city"), comps.get("region"), comps.get("country")]
        joined = ", ".join(str(b) for b in bits if b)
        if joined:
            return joined
    return None


def _published(item: dict[str, Any]) -> datetime:
    raw = item.get("activation_date") or item.get("created_at")
    if raw:
        try:
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def _salary_text(item: dict[str, Any]) -> str | None:
    if not item.get("salary_shown"):
        return None
    lo = item.get("base_salary")
    hi = item.get("maximum_salary")
    if lo is None and hi is None:
        return None
    cur = item.get("salary_currency") or ""
    interval = item.get("salary_interval") or ""
    suffix = f" {cur}".rstrip()
    if interval:
        suffix = f"{suffix}/{interval}".strip("/")
    if lo is not None and hi is not None:
        return f"{lo}-{hi}{suffix}".strip()
    return f"{lo or hi}{suffix}".strip()


def _tags(item: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    if item.get("function"):
        tags.append(str(item["function"]))
    for skill in (item.get("job_sds_skills") or [])[:12]:
        if isinstance(skill, str):
            tags.append(skill)
        elif isinstance(skill, dict) and skill.get("name"):
            tags.append(str(skill["name"]))
    return tags[:15]


def _trim_raw(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item.get("id"),
        "name": item.get("name"),
        "company_name": item.get("company_name"),
        "slug": item.get("slug"),
        "activation_date": item.get("activation_date"),
        "base_salary": item.get("base_salary"),
        "maximum_salary": item.get("maximum_salary"),
        "salary_currency": item.get("salary_currency"),
        "is_work_from_home": item.get("is_work_from_home"),
        "country_code": "PH",
    }
