"""okemprego — free public jobs API for PT/BR/AO (no key; cite canonical URL).

Docs: https://www.okemprego.com/pt/api
Default: Portugal ``it-data`` category (IT / data roles). Optional
``OKEMPREGO_COUNTRIES`` CSV (ISO2 lowercase, default ``pt``).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob, simplify_query_for
from app.core.config import get_settings

API_URL = "https://www.okemprego.com/api/v1/jobs"
DEFAULT_COUNTRIES = ("pt",)
DEFAULT_CATEGORY = "it-data"
PAGE_SIZE = 50
MAX_PAGES = 3
MAX_RECORDS = 150
USER_AGENT = "FMI-MarketIntel/1.0 (okemprego; market-research; +attribution)"


def _countries() -> list[str]:
    raw = (get_settings().okemprego_countries or "").strip()
    if not raw:
        return list(DEFAULT_COUNTRIES)
    out: list[str] = []
    seen: set[str] = set()
    for part in raw.split(","):
        code = part.strip().lower()
        if not code or code in seen:
            continue
        seen.add(code)
        out.append(code)
    return out or list(DEFAULT_COUNTRIES)


def _published(raw: object) -> datetime:
    if raw:
        try:
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def _location(item: dict[str, Any], country: str) -> str:
    bits: list[str] = []
    city = item.get("city")
    if city:
        bits.append(str(city).strip())
    loc = item.get("location")
    if isinstance(loc, dict):
        mun = loc.get("municipality")
        if isinstance(mun, dict) and mun.get("name"):
            name = str(mun["name"]).strip()
            if name and name not in bits:
                bits.append(name)
        dist = loc.get("district")
        if isinstance(dist, dict) and dist.get("name"):
            name = str(dist["name"]).strip()
            if name and name not in bits:
                bits.append(name)
    bits.append(country.upper())
    return ", ".join(bits)


def _salary(item: dict[str, Any]) -> str | None:
    sal = item.get("salary")
    if not isinstance(sal, dict):
        return None
    lo, hi = sal.get("min"), sal.get("max")
    if lo is None and hi is None:
        return None
    cur = sal.get("currency") or ""
    period = sal.get("period") or ""
    return f"{lo or '?'}-{hi or '?'} {cur} / {period}".strip()


def _remote_hint(raw: object) -> bool | None:
    if raw == "full":
        return True
    if raw in {"hybrid", "onsite"}:
        return False
    return None


def _map_job(item: dict[str, Any], country: str) -> RawJob | None:
    job_id = item.get("id") or item.get("slug")
    title = (item.get("title") or "").strip()
    url = (item.get("url") or "").strip()
    if not job_id or not title or not url:
        return None
    tags: list[str] = []
    for key in ("category", "industry", "experienceLevel", "hoursType", "contractType"):
        val = item.get(key)
        if val:
            tags.append(str(val))
    skills = item.get("skills")
    if isinstance(skills, list):
        tags.extend(str(s) for s in skills[:10] if s)
    iso = str(item.get("country") or country).upper()
    return RawJob(
        source_job_id=str(job_id),
        url=url,
        title=title,
        company=item.get("company"),
        description=item.get("description"),
        location=_location(item, iso),
        published_at=_published(item.get("postedAt")),
        salary_text=_salary(item),
        tags=tags[:15],
        job_type=item.get("hoursType") or item.get("contractType"),
        remote_hint=_remote_hint(item.get("remote")),
        raw={
            "country": iso,
            "country_code": iso,
            "slug": item.get("slug"),
            "category": item.get("category"),
            "mode": "public_api",
            "attribution": "okemprego",
        },
    )


class OkEmpregoCollector(BaseCollector):
    name = "okemprego"
    source_key = "okemprego"
    collection_mode = "dump"
    base_url = API_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        q = simplify_query_for(self, query or "")
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        errors: list[str] = []
        records: list[RawJob] = []
        seen: set[str] = set()
        pages = 0

        async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
            for country in _countries():
                if len(records) >= MAX_RECORDS:
                    break
                for page in range(1, MAX_PAGES + 1):
                    if len(records) >= MAX_RECORDS:
                        break
                    params: dict[str, str | int] = {
                        "country": country.upper(),
                        "category": DEFAULT_CATEGORY,
                        "perPage": PAGE_SIZE,
                        "page": page,
                        "sort": "newest",
                    }
                    if q:
                        params["q"] = q
                    try:
                        resp = await client.get(API_URL, params=params)
                        resp.raise_for_status()
                        payload = resp.json() or {}
                    except Exception as exc:  # noqa: BLE001
                        errors.append(f"{country}: {exc}")
                        break

                    pages += 1
                    jobs = payload.get("data") if isinstance(payload, dict) else None
                    if not isinstance(jobs, list):
                        errors.append(f"{country}: unexpected payload")
                        break
                    for item in jobs:
                        if len(records) >= MAX_RECORDS:
                            break
                        if not isinstance(item, dict):
                            continue
                        mapped = _map_job(item, country)
                        if mapped is None or mapped.source_job_id in seen:
                            continue
                        seen.add(mapped.source_job_id)
                        records.append(mapped)

                    pag = payload.get("pagination") if isinstance(payload, dict) else {}
                    total_pages = int(pag.get("totalPages") or 1) if isinstance(pag, dict) else 1
                    if page >= total_pages or not jobs:
                        break

        return CollectorResult(
            records=records, pages_scanned=max(pages, 1), errors=errors
        )
