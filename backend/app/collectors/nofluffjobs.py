"""NoFluffJobs — public posting dump (CEE IT). Prefer query filter; cap records.

The public endpoint returns a large JSON dump (~all open postings). We filter
client-side and cap results so ingest stays bounded. Prefer DevITJobs for lighter
UK/global polls when CEE coverage is not required.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob

MAX_RECORDS = 100


class NoFluffJobsCollector(BaseCollector):
    name = "NoFluffJobs"
    source_key = "nofluffjobs"
    collection_mode = "dump"
    base_url = "https://nofluffjobs.com/api/posting"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        q = (query or "").strip().lower()
        headers = {
            "User-Agent": "FMI-MarketIntel/1.0",
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
        }
        errors: list[str] = []
        try:
            async with httpx.AsyncClient(timeout=90.0, headers=headers) as client:
                resp = await client.get(self.base_url)
                resp.raise_for_status()
                payload = resp.json() or {}
        except Exception as exc:  # noqa: BLE001
            return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        postings = payload.get("postings") if isinstance(payload, dict) else None
        if not isinstance(postings, list):
            return CollectorResult(
                records=[], pages_scanned=1, errors=["unexpected payload"]
            )

        records: list[RawJob] = []
        for item in postings:
            if len(records) >= MAX_RECORDS:
                break
            if not isinstance(item, dict):
                continue
            if q and not _matches(item, q):
                continue
            job_id = item.get("id")
            slug = item.get("url") or job_id
            title = item.get("title") or "Untitled"
            if not job_id or not slug:
                continue
            url = f"https://nofluffjobs.com/pl/job/{slug}"
            published = _posted_at(item)
            loc = _location(item)
            salary = _salary_text(item)
            tags = _tags(item)
            contract = None
            sal = item.get("salary")
            if isinstance(sal, dict) and sal.get("type"):
                contract = str(sal["type"])
            records.append(
                RawJob(
                    source_job_id=str(job_id),
                    url=url,
                    title=title,
                    company=item.get("name"),
                    description=None,
                    location=loc,
                    published_at=published,
                    salary_text=salary,
                    tags=tags,
                    job_type=contract,
                    remote_hint=_remote_hint(item),
                    raw=_trim_raw(item),
                )
            )

        if not records and q:
            errors.append(f"no matches for query={q!r} in first dump scan")
        return CollectorResult(records=records, pages_scanned=1, errors=errors)


def _matches(item: dict[str, Any], q: str) -> bool:
    tile_vals = []
    tiles = item.get("tiles")
    if isinstance(tiles, dict):
        for row in tiles.get("values") or []:
            if isinstance(row, dict) and row.get("value"):
                tile_vals.append(str(row["value"]))
    parts = [
        item.get("title"),
        item.get("name"),
        item.get("category"),
        " ".join(tile_vals),
        " ".join(str(s) for s in (item.get("seniority") or [])),
    ]
    hay = " ".join(str(x) for x in parts if x).lower()
    return q in hay


def _posted_at(item: dict[str, Any]) -> datetime:
    ms = item.get("posted") or item.get("renewed")
    if isinstance(ms, (int, float)) and ms > 0:
        try:
            return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            pass
    return datetime.now(timezone.utc)


def _location(item: dict[str, Any]) -> str | None:
    loc = item.get("location") or {}
    if not isinstance(loc, dict):
        return None
    places = loc.get("places") or []
    bits: list[str] = []
    if places and isinstance(places[0], dict):
        city = places[0].get("city")
        country = (places[0].get("country") or {}).get("code")
        if city:
            bits.append(str(city))
        if country:
            bits.append(str(country).upper())
    if loc.get("fullyRemote"):
        bits.append("Remote")
    elif loc.get("type"):
        bits.append(str(loc["type"]))
    return ", ".join(bits) or None


def _salary_text(item: dict[str, Any]) -> str | None:
    salary = item.get("salary")
    if not isinstance(salary, dict):
        return None
    lo = salary.get("from")
    hi = salary.get("to")
    if lo is None and hi is None:
        return None
    cur = salary.get("currency") or "PLN"
    period = salary.get("period") or ""
    contract = salary.get("type") or ""
    return f"{lo or '?'}-{hi or '?'} {cur}/{period} ({contract})".strip()


def _tags(item: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    if item.get("category"):
        tags.append(str(item["category"]))
    tiles = item.get("tiles")
    if isinstance(tiles, dict):
        for row in tiles.get("values") or []:
            if isinstance(row, dict) and row.get("type") == "requirement" and row.get("value"):
                tags.append(str(row["value"]))
    seniority = item.get("seniority")
    if isinstance(seniority, list):
        tags.extend(str(s) for s in seniority[:3])
    elif seniority:
        tags.append(str(seniority))
    return tags[:20]


def _remote_hint(item: dict[str, Any]) -> bool | None:
    if item.get("fullyRemote"):
        return True
    loc = item.get("location") or {}
    if not isinstance(loc, dict):
        return None
    if loc.get("fullyRemote"):
        return True
    t = str(loc.get("type") or "").lower()
    if t == "remote":
        return True
    if t in {"office", "hybrid"}:
        return False
    return None


def _trim_raw(item: dict[str, Any]) -> dict[str, Any]:
    """Drop heavy logo blobs from persisted raw payload."""
    out = {k: v for k, v in item.items() if k != "logo"}
    out["country_code"] = "PL"
    return out
