from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob


class TheMuseCollector(BaseCollector):
    name = "The Muse"
    source_key = "themuse"
    collection_mode = "dump"
    base_url = "https://www.themuse.com/api/public/jobs"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        errors: list[str] = []
        records: list[RawJob] = []
        params: dict[str, str | int] = {
            "page": 0,
            "category": "Software Engineering",
            "level": "Senior Level",
        }
        if query:
            params["page"] = 0
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
            try:
                resp = await client.get(self.base_url, params=params)
                resp.raise_for_status()
                payload = resp.json()
            except Exception as exc:  # noqa: BLE001
                return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        q = (query or "").lower().strip()
        for item in payload.get("results") or []:
            title = item.get("name") or "Untitled"
            company = (item.get("company") or {}).get("name")
            locs = item.get("locations") or []
            location = ", ".join(loc.get("name") for loc in locs if loc.get("name")) or None
            contents = item.get("contents") or ""
            if q and q not in title.lower() and q not in contents.lower():
                continue
            pub = item.get("publication_date")
            published = datetime.now(timezone.utc)
            if pub:
                try:
                    published = datetime.fromisoformat(str(pub).replace("Z", "+00:00"))
                except ValueError:
                    errors.append(f"invalid date for {item.get('id')}")
            refs = item.get("refs") or {}
            records.append(
                RawJob(
                    source_job_id=str(item.get("id")),
                    url=refs.get("landing_page") or "",
                    title=title,
                    company=company,
                    description=contents,
                    location=location,
                    published_at=published,
                    tags=[c.get("name") for c in (item.get("categories") or []) if c.get("name")],
                    remote_hint=None,
                    raw=item,
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=errors)
