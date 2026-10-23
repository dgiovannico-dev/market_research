"""Le Forem (Wallonia, BE) — ODWB open-data job offers (Opendatasoft Explore API).

Dataset: ``offres-d-emploi-forem`` on https://www.odwb.be/
No partner key for this open dataset. Partner HR-XML / VDAB APIs are out of scope.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob

DATASET_ID = "offres-d-emploi-forem"
BASE_URL = (
    f"https://www.odwb.be/api/explore/v2.1/catalog/datasets/{DATASET_ID}/records"
)
PAGE_SIZE = 100
MAX_RECORDS = 200
DETAIL_FALLBACK = "https://www.leforem.be/recherche-offres/offre-detail/{ref}"


class LeForemCollector(BaseCollector):
    name = "Le Forem"
    source_key = "le_forem"
    collection_mode = "dump"
    base_url = BASE_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        q = (query or "").strip().lower()
        headers = {
            "User-Agent": "FMI-MarketIntel/1.0",
            "Accept": "application/json",
        }
        records: list[RawJob] = []
        errors: list[str] = []
        pages = 0
        offset = 0

        async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
            while len(records) < MAX_RECORDS:
                limit = min(PAGE_SIZE, MAX_RECORDS - len(records))
                try:
                    resp = await client.get(
                        BASE_URL,
                        params={"limit": limit, "offset": offset},
                    )
                    resp.raise_for_status()
                    payload = resp.json() or {}
                except Exception as exc:  # noqa: BLE001
                    if pages == 0:
                        return CollectorResult(
                            records=[], pages_scanned=1, errors=[str(exc)]
                        )
                    errors.append(str(exc))
                    break

                pages += 1
                results = payload.get("results") if isinstance(payload, dict) else None
                if not isinstance(results, list):
                    errors.append("unexpected payload")
                    break
                if not results:
                    break

                for item in results:
                    if len(records) >= MAX_RECORDS:
                        break
                    if not isinstance(item, dict):
                        continue
                    mapped = _map_record(item)
                    if mapped is None:
                        continue
                    if q and not _matches(item, q):
                        continue
                    records.append(mapped)

                if len(results) < limit:
                    break
                offset += limit
                if pages >= 3:
                    break

        return CollectorResult(
            records=records, pages_scanned=max(pages, 1), errors=errors
        )


def _map_record(item: dict[str, Any]) -> RawJob | None:
    ref = item.get("numerooffreforem")
    title = item.get("titreoffre") or "Untitled"
    if not ref:
        return None
    url = item.get("url") or DETAIL_FALLBACK.format(ref=ref)
    return RawJob(
        source_job_id=str(ref),
        url=str(url),
        title=str(title),
        company=_as_str(item.get("nomemployeur")),
        description=_description(item),
        location=_location(item),
        published_at=_published(item.get("datedebutdiffusion")),
        salary_text=None,
        tags=_tags(item),
        job_type=_as_str(item.get("typecontrat")),
        remote_hint=_remote_hint(item),
        raw=_trim_raw(item),
    )


def _matches(item: dict[str, Any], q: str) -> bool:
    hay = " ".join(
        [
            str(item.get("titreoffre") or ""),
            str(item.get("nomemployeur") or ""),
            str(item.get("metier") or ""),
            " ".join(_as_str_list(item.get("secteurs"))),
            " ".join(_as_str_list(item.get("lieuxtravaillocalite"))),
        ]
    ).lower()
    return q in hay


def _location(item: dict[str, Any]) -> str:
    """Always include Belgium so ingest classification can set country_code=BE."""
    locals_ = _as_str_list(item.get("lieuxtravaillocalite"))
    regions = _as_str_list(item.get("lieuxtravailregion"))
    bits = locals_[:2]
    if not bits and regions:
        bits = [r for r in regions if r.upper() != "BELGIQUE"][:2]
    bits.append("Belgium")
    return ", ".join(bits)


def _description(item: dict[str, Any]) -> str | None:
    parts: list[str] = []
    if item.get("metier"):
        parts.append(str(item["metier"]))
    if item.get("typecontrat"):
        parts.append(str(item["typecontrat"]))
    if item.get("regimetravail"):
        parts.append(str(item["regimetravail"]))
    secteurs = _as_str_list(item.get("secteurs"))
    if secteurs:
        parts.append("; ".join(secteurs[:5]))
    return " — ".join(parts) if parts else None


def _tags(item: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    if item.get("metier"):
        tags.append(str(item["metier"]))
    tags.extend(_as_str_list(item.get("secteurs"))[:8])
    tags.extend(_as_str_list(item.get("langues"))[:4])
    if item.get("metiercodedimeco"):
        tags.append(str(item["metiercodedimeco"]))
    seen: set[str] = set()
    out: list[str] = []
    for t in tags:
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out[:20]


def _remote_hint(item: dict[str, Any]) -> bool | None:
    regime = str(item.get("regimetravail") or "").lower()
    if not regime:
        return None
    if "télétravail" in regime or "teletravail" in regime or "remote" in regime:
        return True
    return None


def _published(raw: Any) -> datetime:
    if raw:
        text = str(raw).strip()
        try:
            if len(text) == 10 and text[4] == "-":
                return datetime(
                    int(text[0:4]), int(text[5:7]), int(text[8:10]), tzinfo=timezone.utc
                )
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            pass
    return datetime.now(timezone.utc)


def _as_str(val: Any) -> str | None:
    if val is None:
        return None
    text = str(val).strip()
    return text or None


def _as_str_list(val: Any) -> list[str]:
    if isinstance(val, list):
        return [str(x).strip() for x in val if x is not None and str(x).strip()]
    if isinstance(val, str) and val.strip():
        return [p.strip() for p in val.split(";") if p.strip()]
    return []


def _trim_raw(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "numerooffreforem": item.get("numerooffreforem"),
        "titreoffre": item.get("titreoffre"),
        "nomemployeur": item.get("nomemployeur"),
        "url": item.get("url"),
        "typecontrat": item.get("typecontrat"),
        "regimetravail": item.get("regimetravail"),
        "lieuxtravaillocalite": item.get("lieuxtravaillocalite"),
        "lieuxtravailregion": item.get("lieuxtravailregion"),
        "datedebutdiffusion": item.get("datedebutdiffusion"),
        "metier": item.get("metier"),
        "secteurs": item.get("secteurs"),
    }
