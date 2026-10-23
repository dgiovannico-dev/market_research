"""Jobindex.dk — free public Danish jobs RSS (no key)."""

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
RSS_URL = "https://www.jobindex.dk/jobsoegning.rss"
MAX_RECORDS = 50


class JobindexCollector(BaseCollector):
    name = "Jobindex"
    source_key = "jobindex"
    collection_mode = "feed"
    base_url = RSS_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        q = (query or "").strip()
        headers = {
            "User-Agent": "FMI-MarketIntel/1.0",
            "Accept": "application/rss+xml, application/xml, text/xml",
        }
        params = {"q": q} if q else None
        try:
            async with httpx.AsyncClient(timeout=45.0, headers=headers, follow_redirects=True) as client:
                resp = await client.get(RSS_URL, params=params)
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
            if not link:
                continue
            desc = item.findtext("description") or ""
            company, role = _split_title(title)
            records.append(
                RawJob(
                    source_job_id=_job_id(link, item.findtext("guid")),
                    url=link,
                    title=role or title,
                    company=company,
                    description=_TAG_RE.sub(" ", desc).strip() or None,
                    location="Denmark",
                    published_at=_published(item.findtext("pubDate")),
                    salary_text=None,
                    tags=[],
                    job_type=None,
                    remote_hint=None,
                    raw={"title": title, "link": link, "country_code": "DK"},
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=[])


def _split_title(title: str) -> tuple[str | None, str | None]:
    # Often "Role title, Company"
    if "," not in title:
        return None, title
    role, company = title.rsplit(",", 1)
    company = company.strip() or None
    role = role.strip() or title
    return company, role


def _job_id(link: str, guid: str | None) -> str:
    path = urlparse(link).path or ""
    m = re.search(r"/vis-job/([a-zA-Z0-9]+)", path) or re.search(r"/(\d+)$", path)
    if m:
        return m.group(1)
    if guid:
        m2 = re.search(r"/(\d+)$", guid)
        if m2:
            return m2.group(1)
        return guid
    return link


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
