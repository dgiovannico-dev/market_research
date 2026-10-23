"""HelloWorld.rs — free Serbian IT jobs RSS (no key)."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional
from urllib.parse import urlparse, urlunparse

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob

_TAG_RE = re.compile(r"<[^>]+>")
RSS_URL = "https://helloworld.rs/rss"
MAX_RECORDS = 40


class HelloworldRsCollector(BaseCollector):
    name = "HelloWorld.rs"
    source_key = "helloworld_rs"
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
            company = _company_from_desc(desc)
            records.append(
                RawJob(
                    source_job_id=_job_id(link),
                    url=_clean_url(link),
                    title=title,
                    company=company,
                    description=_TAG_RE.sub(" ", desc).strip() or None,
                    location="Serbia",
                    published_at=_published(item.findtext("pubDate")),
                    salary_text=None,
                    tags=["IT"],
                    job_type=None,
                    remote_hint=None,
                    raw={"title": title, "link": link, "country_code": "RS"},
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=[])


def _company_from_desc(desc: str) -> str | None:
    text = _TAG_RE.sub(" ", desc).strip()
    if " - " in text:
        return text.split(" - ", 1)[0].strip() or None
    return None


def _job_id(link: str) -> str:
    path = urlparse(link).path or ""
    m = re.search(r"/(\d+)/?$", path) or re.search(r"/(\d+)\?", link)
    return m.group(1) if m else link


def _clean_url(link: str) -> str:
    parsed = urlparse(link)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))


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
