from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob


class RemotiveCollector(BaseCollector):
    name = "Remotive"
    source_key = "remotive"
    collection_mode = "dump"
    base_url = "https://remotive.com/api/remote-jobs"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        params = {"category": "software-dev"}
        if query:
            params["search"] = query
        errors: list[str] = []
        records: list[RawJob] = []
        async with httpx.AsyncClient(timeout=45.0) as client:
            try:
                resp = await client.get(self.base_url, params=params)
                resp.raise_for_status()
                payload = resp.json()
            except Exception as exc:  # noqa: BLE001
                return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        for item in payload.get("jobs", []):
            published = None
            if item.get("publication_date"):
                try:
                    published = datetime.fromisoformat(
                        item["publication_date"].replace("Z", "+00:00")
                    )
                    if published.tzinfo is None:
                        published = published.replace(tzinfo=timezone.utc)
                except ValueError:
                    published = None
                    errors.append(f"invalid date for job {item.get('id')}")
            records.append(
                RawJob(
                    source_job_id=str(item.get("id")),
                    url=item.get("url") or "",
                    title=item.get("title") or "Untitled",
                    company=item.get("company_name"),
                    description=item.get("description"),
                    location=item.get("candidate_required_location"),
                    published_at=published or datetime.now(timezone.utc),
                    salary_text=item.get("salary") or None,
                    tags=list(item.get("tags") or []),
                    job_type=item.get("job_type"),
                    remote_hint=True,
                    raw=item,
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=errors)
