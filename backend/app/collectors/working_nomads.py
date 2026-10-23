from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob


class WorkingNomadsCollector(BaseCollector):
    name = "Working Nomads"
    source_key = "working_nomads"
    collection_mode = "dump"
    base_url = "https://www.workingnomads.com/api/exposed_jobs/"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        errors: list[str] = []
        records: list[RawJob] = []
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
            try:
                resp = await client.get(self.base_url)
                resp.raise_for_status()
                payload = resp.json()
            except Exception as exc:  # noqa: BLE001
                return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        if not isinstance(payload, list):
            return CollectorResult(records=[], errors=["unexpected payload shape"])

        q = (query or "").lower().strip()
        for item in payload:
            if not isinstance(item, dict):
                continue
            title = item.get("title") or "Untitled"
            if q and q not in title.lower() and q not in (item.get("description") or "").lower():
                continue
            pub = item.get("pub_date") or item.get("published")
            published = None
            if pub:
                try:
                    published = datetime.fromisoformat(str(pub).replace("Z", "+00:00"))
                except ValueError:
                    errors.append(f"invalid date for {item.get('id') or item.get('url')}")
            sid = str(item.get("id") or item.get("url") or title)
            records.append(
                RawJob(
                    source_job_id=sid,
                    url=item.get("url") or "",
                    title=title,
                    company=item.get("company_name") or item.get("company"),
                    description=item.get("description"),
                    location=item.get("location") or "Remote",
                    published_at=published or datetime.now(timezone.utc),
                    salary_text=item.get("salary") or None,
                    tags=list(item.get("tags") or []),
                    remote_hint=True,
                    raw=item,
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=errors)
