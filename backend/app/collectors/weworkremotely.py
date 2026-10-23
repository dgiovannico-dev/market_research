from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob

_TAG_RE = re.compile(r"<[^>]+>")


class WeWorkRemotelyCollector(BaseCollector):
    name = "We Work Remotely"
    source_key = "weworkremotely"
    collection_mode = "feed"
    base_url = "https://weworkremotely.com/categories/remote-programming-jobs.rss"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        errors: list[str] = []
        records: list[RawJob] = []
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/rss+xml, application/xml"}
        async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
            try:
                resp = await client.get(self.base_url)
                resp.raise_for_status()
                root = ET.fromstring(resp.text)
            except Exception as exc:  # noqa: BLE001
                return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        q = (query or "").lower().strip()
        for item in root.findall("./channel/item"):
            title = (item.findtext("title") or "Untitled").strip()
            link = (item.findtext("link") or "").strip()
            desc = item.findtext("description") or ""
            if q and q not in title.lower() and q not in desc.lower():
                continue
            pub_raw = item.findtext("pubDate")
            published = datetime.now(timezone.utc)
            if pub_raw:
                try:
                    published = parsedate_to_datetime(pub_raw)
                    if published.tzinfo is None:
                        published = published.replace(tzinfo=timezone.utc)
                except (TypeError, ValueError):
                    errors.append(f"invalid pubDate for {link}")
            guid = item.findtext("guid") or link or title
            company = None
            if ":" in title:
                company, title = [p.strip() for p in title.split(":", 1)]
            records.append(
                RawJob(
                    source_job_id=guid,
                    url=link,
                    title=title,
                    company=company,
                    description=_TAG_RE.sub(" ", desc).strip() or None,
                    location="Remote",
                    published_at=published,
                    remote_hint=True,
                    raw={"title": title, "link": link},
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=errors)
