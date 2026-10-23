"""Dev Global Jobs — free public display API (attribution required; no key).

Docs: https://devglobaljobs.com/developers
Priority geo: LU / BG (and optional extra ISO codes via DEVGLOBALJOBS_COUNTRIES).
Rate limit: 120 req/min/IP. Keep source attribution on displayed listings.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob, simplify_query_for
from app.core.config import get_settings

API_URL = "https://devglobaljobs.com/api/v1/jobs"
DEFAULT_COUNTRIES = ("lu", "bg")
PAGE_SIZE = 50
MAX_PAGES_PER_COUNTRY = 2
MAX_RECORDS = 200
USER_AGENT = "FMI-MarketIntel/1.0 (devglobaljobs; market-research; +attribution)"


def _countries() -> list[str]:
    raw = (get_settings().devglobaljobs_countries or "").strip()
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


def _map_job(item: dict[str, Any], country: str) -> RawJob | None:
    """Map API row; ``country`` is the request ISO2 (always tags Job.country_code)."""
    job_id = item.get("id")
    title = (item.get("title") or "").strip()
    url = (item.get("url") or "").strip()
    if not job_id or not title or not url:
        return None
    iso = (country or "").strip().lower()
    iso2 = iso.upper() if len(iso) == 2 and iso.isalpha() else ""
    tags: list[str] = []
    for key in ("category", "skillCategory", "jobType"):
        val = item.get(key)
        if val and str(val).strip():
            tags.append(str(val).strip())
    loc = (item.get("location") or "").strip() or (iso2 or "unknown")
    if iso2 and iso2 not in loc.upper():
        loc = f"{loc} ({iso2})"
    remote = None
    cat = str(item.get("category") or "").lower()
    if "remote" in cat or "remote" in loc.lower():
        remote = True
    # Prefer request ISO2 over payload ``country`` (may be a name → unknown).
    raw: dict[str, Any] = {
        "category": item.get("category"),
        "skillCategory": item.get("skillCategory"),
        "mode": "public_api",
        "attribution": "Dev Global Jobs",
        "api_country": item.get("country"),
    }
    if iso2:
        raw["country_code"] = iso2
        raw["country"] = iso2
    return RawJob(
        source_job_id=str(job_id),
        url=url,
        title=title,
        company=item.get("organization"),
        description=item.get("descriptionExcerpt"),
        location=loc,
        published_at=_published(item.get("postedAt")),
        salary_text=(str(item["salary"]).strip() if item.get("salary") else None),
        tags=tags[:12],
        job_type=item.get("jobType"),
        remote_hint=remote,
        raw=raw,
    )


class DevGlobalJobsCollector(BaseCollector):
    name = "Dev Global Jobs"
    source_key = "devglobaljobs"
    collection_mode = "dump"
    base_url = API_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        q = simplify_query_for(self, query or "")
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        errors: list[str] = []
        records: list[RawJob] = []
        seen: set[str] = set()
        pages = 0
        countries = _countries()

        async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
            for country in countries:
                if len(records) >= MAX_RECORDS:
                    break
                for page in range(MAX_PAGES_PER_COUNTRY):
                    if len(records) >= MAX_RECORDS:
                        break
                    params: dict[str, str | int] = {
                        "country": country,
                        "limit": PAGE_SIZE,
                        "offset": page * PAGE_SIZE,
                    }
                    if q:
                        params["search"] = q
                    try:
                        resp = await client.get(API_URL, params=params)
                        resp.raise_for_status()
                        payload = resp.json() or {}
                    except Exception as exc:  # noqa: BLE001
                        errors.append(f"{country}: {exc}")
                        break

                    pages += 1
                    jobs = payload.get("jobs") if isinstance(payload, dict) else None
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

                    meta = payload.get("meta") if isinstance(payload, dict) else {}
                    has_more = bool(meta.get("hasMore")) if isinstance(meta, dict) else False
                    if not jobs or not has_more:
                        break

        return CollectorResult(
            records=records, pages_scanned=max(pages, 1), errors=errors
        )
