"""MPSV / Úřad práce ČR — Volná místa open-data dump (collection_mode=dump).

Documented JSON URL (daily):
  https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json
As of 2026-10-21 that path returns HTTP 404; the live dump is the JSON-LD twin
(~180MB). Collector tries JSON first, then streams JSON-LD with a bounded IT
keyword filter so we never materialize the full file.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterable
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob
from app.collectors.mpsv_stream import empty_aiter, iter_polozky_payload, iter_polozky_stream

DUMP_JSON_URL = "https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json"
DUMP_JSONLD_URL = "https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.jsonld"
DATASET_PAGE = "https://data.mpsv.cz/web/data/volna-mista-za-celou-cr"
RESOURCE_BASE = "https://data.mpsv.cz/zdroj/"

MAX_RECORDS = 300
MAX_SCAN = 12_000
MAX_BYTES = 40_000_000

# Applied when query is blank — dump is country-wide and huge.
DEFAULT_IT_KEYWORDS = (
    "programátor",
    "programator",
    "vývojář",
    "vyvojar",
    "developer",
    "software",
    "softwar",
    "informatik",
    "datov",
    "systémov",
    "systemov",
    "devops",
    "webov",
    "aplikac",
    "databáz",
    "databaz",
    "kyber",
    "cyber",
    "javascript",
    "typescript",
    "python",
    "java",
    "php",
    ".net",
    "c#",
    "sql",
    "frontend",
    "backend",
    "fullstack",
    "full-stack",
    "tester softwar",
    "qa engineer",
    "ict",
    "it specialista",
    "it analytik",
    "administrátor it",
    "administrator it",
    "machine learning",
    "artificial intelligence",
)


class MpsvCollector(BaseCollector):
    # Must match catalog.json name so seed merges by name (avoids dup stub rows).
    name = "MPSV / Úřad práce — Volná místa"
    source_key = "mpsv"
    collection_mode = "dump"
    base_url = DUMP_JSON_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        q = (query or "").strip().lower()
        filter_terms = _filter_terms(q)
        headers = {
            "User-Agent": "FMI-MarketIntel/1.0 (+market_research; open-data ingest)",
            "Accept": "application/json, application/ld+json;q=0.9, */*;q=0.1",
        }
        errors: list[str] = []
        records: list[RawJob] = []
        scanned = 0
        source_used = ""

        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(120.0, connect=30.0),
                headers=headers,
                follow_redirects=True,
            ) as client:
                items, source_used, fetch_err = await _open_dump_stream(client)
                if fetch_err:
                    return CollectorResult(
                        records=[], pages_scanned=1, errors=[fetch_err]
                    )
                async for item in items:
                    scanned += 1
                    if scanned > MAX_SCAN:
                        errors.append(f"scan_cap:{MAX_SCAN}")
                        break
                    if not isinstance(item, dict):
                        continue
                    if filter_terms and not _matches(item, filter_terms):
                        continue
                    mapped = _map_record(item)
                    if mapped is None:
                        continue
                    records.append(mapped)
                    if len(records) >= MAX_RECORDS:
                        break
        except Exception as exc:  # noqa: BLE001
            return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        if not records and not errors:
            errors.append(
                "no_matching_records "
                f"(source={source_used or 'none'}; filter={filter_terms[:5]!r}; "
                f"scanned={scanned}). See {DATASET_PAGE}"
            )
        return CollectorResult(records=records, pages_scanned=1, errors=errors)


def _filter_terms(query: str) -> tuple[str, ...]:
    if query:
        parts = [p.strip() for p in query.replace(",", " ").split() if p.strip()]
        return tuple(parts) if parts else DEFAULT_IT_KEYWORDS
    return DEFAULT_IT_KEYWORDS


def _matches(item: dict[str, Any], terms: Iterable[str]) -> bool:
    hay = _haystack(item)
    return any(term in hay for term in terms)


def _haystack(item: dict[str, Any]) -> str:
    emp = item.get("zamestnavatel")
    isco = item.get("profeseCzIsco")
    bits = [
        _cs(item.get("pozadovanaProfese")),
        _cs(item.get("upresnujiciInformace")),
        str(emp.get("nazev") or "") if isinstance(emp, dict) else "",
        str(isco.get("id") or "") if isinstance(isco, dict) else "",
    ]
    return " ".join(b for b in bits if b).lower()


def _cs(val: Any) -> str:
    if isinstance(val, dict):
        return str(val.get("cs") or "")
    return str(val or "")


def _map_record(item: dict[str, Any]) -> RawJob | None:
    portal_id = item.get("portalId")
    ref = item.get("referencniCislo")
    job_id = portal_id or ref or item.get("id")
    title = _cs(item.get("pozadovanaProfese")).strip() or "Untitled"
    if not job_id:
        return None
    company = None
    emp = item.get("zamestnavatel")
    if isinstance(emp, dict) and emp.get("nazev"):
        company = str(emp["nazev"])
    return RawJob(
        source_job_id=str(job_id),
        url=_job_url(item, job_id),
        title=title,
        company=company,
        description=_description(item),
        location=_location(item),
        published_at=_published(item),
        salary_text=_salary_text(item),
        tags=_tags(item),
        job_type=None,
        remote_hint=_remote_hint(item),
        raw=_trim_raw(item),
    )


def _job_url(item: dict[str, Any], job_id: Any) -> str:
    url = item.get("urlAdresa")
    if isinstance(url, str) and url.startswith("http"):
        return url
    rid = item.get("id")
    if isinstance(rid, str) and rid:
        return RESOURCE_BASE + rid.lstrip("/")
    return f"{RESOURCE_BASE}VolneMisto/{job_id}"


def _description(item: dict[str, Any]) -> str | None:
    text = _cs(item.get("upresnujiciInformace")).strip()
    return text[:4000] if text else None


def _location(item: dict[str, Any]) -> str | None:
    place = item.get("mistoVykonuPrace")
    if not isinstance(place, dict):
        return "Czechia"
    if place.get("adresaText"):
        return str(place["adresaText"])
    sites = place.get("pracoviste") or []
    if isinstance(sites, list) and sites:
        first = sites[0]
        if isinstance(first, dict) and first.get("nazev"):
            return str(first["nazev"])
    return "Czechia"


def _published(item: dict[str, Any]) -> datetime:
    for key in ("datumVlozeni", "datumZmeny"):
        raw = item.get(key)
        if not raw:
            continue
        try:
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except ValueError:
            continue
    return datetime.now(timezone.utc)


def _salary_text(item: dict[str, Any]) -> str | None:
    lo, hi = item.get("mesicniMzdaOd"), item.get("mesicniMzdaDo")
    if lo is None and hi is None:
        return None
    if lo is not None and hi is not None:
        return f"{lo}-{hi} CZK"
    return f"{lo or hi} CZK"


def _tags(item: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    isco = item.get("profeseCzIsco")
    if isinstance(isco, dict) and isco.get("id"):
        tags.append(str(isco["id"]))
    title = _cs(item.get("pozadovanaProfese"))
    if title:
        tags.append(title[:80])
    return tags[:10]


def _remote_hint(item: dict[str, Any]) -> bool | None:
    hay = _haystack(item)
    if any(k in hay for k in ("home office", "práce z domova", "prace z domova", "remote")):
        return True
    return None


def _trim_raw(item: dict[str, Any]) -> dict[str, Any]:
    place = item.get("mistoVykonuPrace")
    return {
        "portalId": item.get("portalId"),
        "referencniCislo": item.get("referencniCislo"),
        "pozadovanaProfese": item.get("pozadovanaProfese"),
        "zamestnavatel": item.get("zamestnavatel"),
        "mesicniMzdaOd": item.get("mesicniMzdaOd"),
        "mesicniMzdaDo": item.get("mesicniMzdaDo"),
        "datumVlozeni": item.get("datumVlozeni"),
        "mistoVykonuPrace": {"adresaText": place.get("adresaText")}
        if isinstance(place, dict)
        else None,
        "country_code": "CZ",
    }


async def _open_dump_stream(
    client: httpx.AsyncClient,
) -> tuple[AsyncIterator[dict[str, Any]], str, str | None]:
    """Try compact JSON, then stream JSON-LD. Fail closed with a clear error."""
    for url, label in ((DUMP_JSON_URL, "json"), (DUMP_JSONLD_URL, "jsonld")):
        try:
            req = client.build_request("GET", url)
            resp = await client.send(req, stream=True)
        except Exception as exc:  # noqa: BLE001
            if label == "jsonld":
                return empty_aiter(), "", f"dump_fetch_failed: {exc}"
            continue
        ctype = (resp.headers.get("content-type") or "").lower()
        if resp.status_code >= 400 or "text/html" in ctype:
            await resp.aclose()
            if label == "jsonld":
                return (
                    empty_aiter(),
                    "",
                    f"dump_unavailable: JSON 404/HTML and JSON-LD status="
                    f"{resp.status_code} ctype={ctype!r}. Dataset: {DATASET_PAGE}",
                )
            continue
        return iter_polozky_stream(resp, max_bytes=MAX_BYTES), label, None
    return (
        empty_aiter(),
        "",
        f"dump_unavailable: neither JSON nor JSON-LD usable. Dataset: {DATASET_PAGE}",
    )


# Re-export for tests
__all__ = [
    "DUMP_JSON_URL",
    "DUMP_JSONLD_URL",
    "MAX_RECORDS",
    "MpsvCollector",
    "iter_polozky_payload",
]
