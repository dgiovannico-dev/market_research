"""Tecnoempleo — free public Spain IT jobs RSS (no key). ADR-003: RSS only, no Empléate scrape."""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional
from urllib.parse import urlparse

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob

_TAG_RE = re.compile(r"<[^>]+>")
_FIELD_RE = re.compile(
    r"<b>(?P<label>[^<:]+):</b>\s*(?:&nbsp;)?\s*(?P<value>.*?)(?=<br\s*/?>|<b>|$)",
    re.I | re.S,
)
# Documented syndication endpoint (help: /ofertas-empleo-rss.php → alertas-empleo-rss.php).
RSS_URL = "https://www.tecnoempleo.com/alertas-empleo-rss.php"
MAX_RECORDS = 80


class TecnoempleoCollector(BaseCollector):
    name = "Tecnoempleo"
    source_key = "tecnoempleo"
    collection_mode = "feed"
    base_url = RSS_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        q = (query or "").strip()
        headers = {
            "User-Agent": "FMI-MarketIntel/1.0",
            "Accept": "application/rss+xml, application/xml, text/xml",
        }
        # Documented keyword filter on the same alert feed (`te=` = tecnologías / search text).
        params = {"te": q} if q else None
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
            fields = _parse_fields(desc)
            company = fields.get("empresa")
            location = fields.get("provincia") or fields.get("población") or "Spain"
            salary_text = fields.get("salario")
            tech = fields.get("tecnologías") or fields.get("tecnologias") or ""
            tags = [t.strip() for t in re.split(r"[,;]", tech) if t.strip()][:12]
            if "IT" not in tags:
                tags = ["IT", *tags]
            remote_hint = _remote_hint(location, desc)
            plain = _TAG_RE.sub(" ", html.unescape(desc)).strip() or None
            records.append(
                RawJob(
                    source_job_id=_job_id(link, item.findtext("guid")),
                    url=link,
                    title=title,
                    company=company,
                    description=plain,
                    location=location,
                    published_at=_published(item.findtext("pubDate")),
                    salary_text=salary_text,
                    tags=tags,
                    job_type=fields.get("tipo de contrato"),
                    remote_hint=remote_hint,
                    raw={"title": title, "link": link, "mode": "rss", "country_code": "ES"},
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=[])


def _parse_fields(desc: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in _FIELD_RE.finditer(desc):
        label = html.unescape(m.group("label")).strip().lower()
        value = _TAG_RE.sub(" ", html.unescape(m.group("value") or "")).strip()
        value = re.sub(r"\s+", " ", value).strip()
        if label and value:
            out[label] = value
    return out


def _remote_hint(location: str | None, desc: str) -> str | None:
    blob = f"{location or ''} {desc}".lower()
    if "remoto" in blob or "remote" in blob:
        return "remote"
    if "híbrido" in blob or "hibrido" in blob or "hybrid" in blob:
        return "hybrid"
    return None


def _job_id(link: str, guid: str | None) -> str:
    for candidate in (link, guid or ""):
        m = re.search(r"/rf-([a-fA-F0-9]+)", candidate)
        if m:
            return m.group(1)
    path = urlparse(link).path or ""
    if path.strip("/"):
        return path.rstrip("/").split("/")[-1]
    return guid or link


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
