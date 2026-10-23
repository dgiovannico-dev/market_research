"""Teamtailor public career JSON Feed (per-host allowlist; no API key)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import urlparse

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob
from app.core.config import get_settings

MAX_PER_TENANT = 40
MAX_PAGES_PER_HOST = 3


def _split_csv(value: str) -> list[str]:
    return [p.strip() for p in value.split(",") if p.strip()]


def _host_label(host: str) -> str:
    return host.strip().lower().removeprefix("https://").removeprefix("http://").rstrip("/")


def _parse_dt(value: Any) -> datetime:
    published = datetime.now(timezone.utc)
    if not value:
        return published
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return published


def _location_from_jobposting(jobposting: dict[str, Any]) -> str | None:
    locs = jobposting.get("jobLocation")
    if locs is None:
        return None
    if isinstance(locs, dict):
        locs = [locs]
    if not isinstance(locs, list):
        return None
    parts: list[str] = []
    for place in locs:
        if not isinstance(place, dict):
            continue
        addr = place.get("address") if isinstance(place.get("address"), dict) else place
        if not isinstance(addr, dict):
            continue
        locality = addr.get("addressLocality")
        country = addr.get("addressCountry")
        region = addr.get("addressRegion")
        chunk = ", ".join(str(p) for p in (locality, region, country) if p)
        if chunk:
            parts.append(chunk)
    return "; ".join(parts) if parts else None


def _job_id(item: dict[str, Any], host: str) -> str:
    jp = item.get("_jobposting") if isinstance(item.get("_jobposting"), dict) else {}
    ident = jp.get("identifier") if isinstance(jp, dict) else None
    if isinstance(ident, dict) and ident.get("value") is not None:
        return f"{host}:{ident['value']}"
    raw_id = item.get("id")
    if raw_id is not None:
        return f"{host}:{raw_id}"
    url = item.get("url") or ""
    path = urlparse(str(url)).path.rstrip("/").split("/")[-1]
    return f"{host}:{path or 'unknown'}"


class TeamtailorCollector(BaseCollector):
    name = "Teamtailor Career Feeds"
    source_key = "teamtailor"
    collection_mode = "dump"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        hosts = [_host_label(h) for h in _split_csv(get_settings().teamtailor_hosts)]
        if not hosts:
            return CollectorResult(records=[], errors=["TEAMTAILOR_HOSTS empty"])
        errors: list[str] = []
        records: list[RawJob] = []
        q = (query or "").lower().strip()
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        pages_scanned = 0

        async with httpx.AsyncClient(timeout=45.0, headers=headers, follow_redirects=True) as client:
            for host in hosts:
                matched = 0
                url: str | None = f"https://{host}/jobs.json"
                feed_company: str | None = None
                for _ in range(MAX_PAGES_PER_HOST):
                    if url is None or matched >= MAX_PER_TENANT:
                        break
                    try:
                        resp = await client.get(url)
                        resp.raise_for_status()
                        payload = resp.json() or {}
                    except Exception as exc:  # noqa: BLE001
                        errors.append(f"{host}: {exc}")
                        break
                    pages_scanned += 1
                    if not isinstance(payload, dict):
                        errors.append(f"{host}: unexpected payload")
                        break
                    if feed_company is None:
                        feed_company = payload.get("title") or host
                    items = payload.get("items") or []
                    if not isinstance(items, list):
                        errors.append(f"{host}: items not a list")
                        break
                    for item in items:
                        if matched >= MAX_PER_TENANT:
                            break
                        if not isinstance(item, dict):
                            continue
                        title = item.get("title") or "Untitled"
                        if q and q not in title.lower():
                            continue
                        jp = item.get("_jobposting") if isinstance(item.get("_jobposting"), dict) else {}
                        hiring = jp.get("hiringOrganization") if isinstance(jp, dict) else None
                        company = feed_company
                        if isinstance(hiring, dict) and hiring.get("name"):
                            company = str(hiring["name"])
                        desc = item.get("content_html")
                        if not desc and isinstance(jp, dict):
                            desc = jp.get("description")
                        records.append(
                            RawJob(
                                source_job_id=_job_id(item, host),
                                url=item.get("url") or "",
                                title=title,
                                company=company,
                                description=desc if isinstance(desc, str) and desc.strip() else None,
                                location=_location_from_jobposting(jp) if isinstance(jp, dict) else None,
                                published_at=_parse_dt(item.get("date_published") or (jp or {}).get("datePosted")),
                                remote_hint=None,
                                raw={
                                    "id": item.get("id"),
                                    "title": title,
                                    "host": host,
                                    "identifier": (jp or {}).get("identifier") if isinstance(jp, dict) else None,
                                },
                            )
                        )
                        matched += 1
                    next_url = payload.get("next_url")
                    url = str(next_url) if next_url else None

        return CollectorResult(records=records, pages_scanned=pages_scanned or len(hosts), errors=errors)
