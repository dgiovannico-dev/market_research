"""Jobweb Kenya — free Kenya jobs RSS (no key)."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional
from urllib.parse import urlparse

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob

_TAG_RE = re.compile(r"<[^>]+>")
RSS_URL = "https://www.jobwebkenya.com/feed/"
MAX_RECORDS = 40


class JobwebKenyaCollector(BaseCollector):
    name = "Jobweb Kenya"
    source_key = "jobweb_kenya"
    collection_mode = "feed"
    base_url = RSS_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        q = (query or "").strip().lower()
        headers = {
            "User-Agent": "FMI-MarketIntel/1.0",
            "Accept": "application/rss+xml, application/xml, text/xml",
        }
        try:
            async with httpx.AsyncClient(timeout=45.0, headers=headers, follow_redirects=True) as client:
                resp = await client.get(RSS_URL)
                resp.raise_for_status()
                root = ET.fromstring(resp.content)
        except Exception as exc:  # noqa: BLE001
            return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        records: list[RawJob] = []
        for item in root.findall("./channel/item"):
            if len(records) >= MAX_RECORDS:
                break
            title = (item.findtext("title") or "Untitled").strip()
            link = (item.findtext("link") or "").strip()
            desc = item.findtext("description") or ""
            if not link:
                continue
            if q and q not in title.lower() and q not in desc.lower():
                continue
            company, role = _split_title(title)
            records.append(
                RawJob(
                    source_job_id=_job_id(link),
                    url=link,
                    title=role or title,
                    company=company,
                    description=_TAG_RE.sub(" ", desc).strip() or None,
                    location="Kenya",
                    published_at=_published(item.findtext("pubDate")),
                    salary_text=None,
                    tags=[],
                    job_type=None,
                    remote_hint=None,
                    raw={"title": title, "link": link},
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=[])


def _split_title(title: str) -> tuple[str | None, str | None]:
    # "Role at Company"
    if " at " not in title.lower():
        return None, title
    idx = title.lower().rfind(" at ")
    role = title[:idx].strip()
    company = title[idx + 4 :].strip()
    return company or None, role or title


def _job_id(link: str) -> str:
    path = (urlparse(link).path or "").rstrip("/")
    slug = path.split("/")[-1] if path else link
    return slug or link


def _published(raw: str | None) -> datetime:
    if raw:
        try:
            dt = parsedate_to_datetime(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (TypeError, ValueError):
            pass
    return datetime.now(timezone.utc)
