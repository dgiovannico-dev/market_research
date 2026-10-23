"""DOU.ua — free Ukrainian IT jobs RSS (category feeds, no key)."""

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
RSS_URL = "https://jobs.dou.ua/vacancies/feeds/"
MAX_RECORDS = 50
_COMPANY_RE = re.compile(r"/companies/([^/]+)/vacancies/")


class DouUaCollector(BaseCollector):
    name = "DOU.ua"
    source_key = "dou_ua"
    collection_mode = "feed"
    base_url = RSS_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        # Feed mode: base RSS without inventing a category; query soft-filters locally.
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
            guid = (item.findtext("guid") or link).strip()
            company, location = _parse_title(title)
            records.append(
                RawJob(
                    source_job_id=_job_id(link, guid),
                    url=_clean_url(link),
                    title=title,
                    company=company or _company_from_url(link),
                    description=_TAG_RE.sub(" ", desc).strip() or None,
                    location=location or "Ukraine",
                    published_at=_published(item.findtext("pubDate")),
                    salary_text=None,
                    tags=[],
                    job_type=None,
                    remote_hint=None,
                    raw={"title": title, "link": link, "country_code": "UA"},
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=[])


def _parse_title(title: str) -> tuple[str | None, str | None]:
    # Typical: "Senior Java Developer в BIScience, Київ"
    if " в " not in title:
        return None, None
    _, rest = title.split(" в ", 1)
    parts = [p.strip() for p in rest.split(",") if p.strip()]
    if not parts:
        return None, None
    if len(parts) == 1:
        return parts[0], None
    return parts[0], parts[-1]


def _company_from_url(link: str) -> str | None:
    m = _COMPANY_RE.search(urlparse(link).path or "")
    if not m:
        return None
    return m.group(1).replace("-", " ").title()


def _job_id(link: str, guid: str) -> str:
    path = urlparse(link).path or ""
    m = re.search(r"/vacancies/(\d+)", path)
    if m:
        return m.group(1)
    return guid


def _clean_url(link: str) -> str:
    # Drop tracking query for stable evidence URLs
    parsed = urlparse(link)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


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
