from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob


class RemoteOKCollector(BaseCollector):
    """Remote OK JSON API. Attribution required per their API legal notice."""

    name = "Remote OK"
    source_key = "remoteok"
    collection_mode = "dump"
    base_url = "https://remoteok.com/api"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        params: dict[str, str] = {}
        if query:
            params["tag"] = query.replace(" ", "-").lower()
        errors: list[str] = []
        records: list[RawJob] = []
        headers = {
            "User-Agent": "FMI-MarketIntel/1.0 (+https://github.com/dgiovannico-dev/market_research)",
            "Accept": "application/json",
        }
        async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
            try:
                resp = await client.get(self.base_url, params=params or None)
                resp.raise_for_status()
                payload = resp.json()
            except Exception as exc:  # noqa: BLE001
                return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        if not isinstance(payload, list):
            return CollectorResult(records=[], errors=["unexpected payload shape"])

        for item in payload:
            if not isinstance(item, dict) or "id" not in item or item.get("legal"):
                continue
            published = None
            epoch = item.get("epoch")
            if epoch is not None:
                try:
                    published = datetime.fromtimestamp(float(epoch), tz=timezone.utc)
                except (TypeError, ValueError, OSError):
                    errors.append(f"invalid epoch for {item.get('id')}")
            if published is None and item.get("date"):
                try:
                    published = datetime.fromisoformat(
                        str(item["date"]).replace("Z", "+00:00")
                    )
                except ValueError:
                    errors.append(f"invalid date for {item.get('id')}")
            tags = item.get("tags") or []
            if isinstance(tags, str):
                tags = [tags]
            salary_text = item.get("salary") or None
            if not salary_text and (item.get("salary_min") or item.get("salary_max")):
                currency = item.get("currency") or "USD"
                salary_text = (
                    f"{item.get('salary_min') or '?'}-{item.get('salary_max') or '?'} "
                    f"{currency}"
                ).strip()
            records.append(
                RawJob(
                    source_job_id=str(item["id"]),
                    url=item.get("url") or item.get("apply_url") or "",
                    title=item.get("position") or item.get("title") or "Untitled",
                    company=item.get("company"),
                    description=item.get("description") or item.get("text"),
                    location=item.get("location") or "Worldwide",
                    published_at=published or datetime.now(timezone.utc),
                    salary_text=salary_text,
                    tags=list(tags),
                    job_type=None,
                    remote_hint=True,
                    raw=item,
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=errors)
