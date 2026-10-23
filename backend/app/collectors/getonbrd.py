"""Get on Board — free public LATAM tech jobs API (no key)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob

SEARCH_URL = "https://www.getonbrd.com/api/v0/search/jobs"
CATEGORY_URL = "https://www.getonbrd.com/api/v0/categories/programming/jobs"
MAX_RECORDS = 80


class GetOnBoardCollector(BaseCollector):
    name = "Get on Board"
    source_key = "getonbrd"
    collection_mode = "dump"
    base_url = SEARCH_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        q = (query or "").strip()
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        errors: list[str] = []
        records: list[RawJob] = []

        async with httpx.AsyncClient(timeout=45.0, headers=headers, follow_redirects=True) as client:
            if q:
                pages = await _fetch_search(client, q, errors)
            else:
                pages = await _fetch_category(client, errors)

        for item in pages:
            if len(records) >= MAX_RECORDS:
                break
            if not isinstance(item, dict):
                continue
            job_id = item.get("id")
            attrs = item.get("attributes") or {}
            if not isinstance(attrs, dict) or not job_id:
                continue
            title = attrs.get("title") or "Untitled"
            links = item.get("links") or {}
            url = ""
            if isinstance(links, dict):
                url = links.get("public_url") or ""
            if not url:
                url = f"https://www.getonbrd.com/jobs/{job_id}"
            published = _published_at(attrs.get("published_at"))
            location = _location(attrs)
            salary_text = _salary_text(attrs)
            tags = _tags(attrs)
            company = _company_label(attrs)
            desc = attrs.get("description") or attrs.get("projects")
            records.append(
                RawJob(
                    source_job_id=str(job_id),
                    url=url,
                    title=title,
                    company=company,
                    description=desc if isinstance(desc, str) else None,
                    location=location,
                    published_at=published,
                    salary_text=salary_text,
                    tags=tags,
                    job_type=None,
                    remote_hint=bool(attrs.get("remote")) if attrs.get("remote") is not None else None,
                    raw=_trim_raw(item),
                )
            )

        return CollectorResult(records=records, pages_scanned=1, errors=errors)


async def _fetch_search(
    client: httpx.AsyncClient, query: str, errors: list[str]
) -> list[dict[str, Any]]:
    try:
        resp = await client.get(SEARCH_URL, params={"query": query, "per_page": 50, "page": 1})
        resp.raise_for_status()
        payload = resp.json() or {}
    except Exception as exc:  # noqa: BLE001
        errors.append(str(exc))
        return []
    data = payload.get("data") if isinstance(payload, dict) else None
    return data if isinstance(data, list) else []


async def _fetch_category(client: httpx.AsyncClient, errors: list[str]) -> list[dict[str, Any]]:
    try:
        resp = await client.get(CATEGORY_URL, params={"per_page": 50, "page": 1})
        resp.raise_for_status()
        payload = resp.json() or {}
    except Exception as exc:  # noqa: BLE001
        errors.append(str(exc))
        return []
    data = payload.get("data") if isinstance(payload, dict) else None
    return data if isinstance(data, list) else []


def _published_at(value: Any) -> datetime:
    if isinstance(value, (int, float)) and value > 0:
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            pass
    return datetime.now(timezone.utc)


def _location(attrs: dict[str, Any]) -> str | None:
    bits: list[str] = []
    countries = attrs.get("countries")
    if isinstance(countries, list):
        bits.extend(str(c) for c in countries[:4] if c)
    cities = attrs.get("location_cities")
    if isinstance(cities, list):
        bits.extend(str(c) for c in cities[:3] if c)
    if attrs.get("remote"):
        zone = attrs.get("remote_zone") or attrs.get("remote_modality")
        bits.append(f"Remote{f' ({zone})' if zone else ''}")
    return ", ".join(bits) or None


def _salary_text(attrs: dict[str, Any]) -> str | None:
    lo = attrs.get("min_salary")
    hi = attrs.get("max_salary")
    if lo is None and hi is None:
        return None
    cur = attrs.get("currency")
    # Do not invent currency when the API leaves it null
    unit = f"{cur}/month" if cur else "month (currency undeclared)"
    return f"{lo or '?'}-{hi or '?'} {unit}"


def _tags(attrs: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    if attrs.get("category_name"):
        tags.append(str(attrs["category_name"]))
    raw_tags = attrs.get("tags")
    if isinstance(raw_tags, list):
        for t in raw_tags[:12]:
            if isinstance(t, dict) and t.get("name"):
                tags.append(str(t["name"]))
            elif isinstance(t, str):
                tags.append(t)
    return tags[:20]


def _company_label(attrs: dict[str, Any]) -> str | None:
    company = attrs.get("company")
    if not isinstance(company, dict):
        return None
    data = company.get("data")
    if isinstance(data, dict) and data.get("id") is not None:
        return f"company:{data['id']}"
    return None


def _trim_raw(item: dict[str, Any]) -> dict[str, Any]:
    attrs = item.get("attributes")
    if not isinstance(attrs, dict):
        return {"id": item.get("id")}
    keep = {
        k: attrs.get(k)
        for k in (
            "title",
            "min_salary",
            "max_salary",
            "currency",
            "remote",
            "remote_modality",
            "countries",
            "category_name",
            "published_at",
            "seniority",
        )
    }
    return {"id": item.get("id"), "attributes": keep, "links": item.get("links")}
