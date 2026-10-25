"""Rules extract for market certifications (SPEC-certifications)."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
_TAXONOMY_PATH = _REPO_ROOT / "data" / "taxonomies" / "certifications.json"


@lru_cache(maxsize=1)
def load_cert_taxonomy() -> list[dict[str, Any]]:
    if not _TAXONOMY_PATH.is_file():
        return []
    data = json.loads(_TAXONOMY_PATH.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def _patterns(entry: dict[str, Any]) -> list[re.Pattern[str]]:
    names = [str(entry.get("display_name") or "")]
    names.extend(str(a) for a in (entry.get("aliases") or []))
    out: list[re.Pattern[str]] = []
    for name in names:
        name = name.strip()
        if not name:
            continue
        # Word-ish boundaries; allow + and – inside names
        escaped = re.escape(name).replace(r"\ ", r"[\s\-–—]+")
        out.append(re.compile(rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])", re.IGNORECASE))
    return out


@lru_cache(maxsize=1)
def _compiled() -> list[tuple[str, str, list[re.Pattern[str]]]]:
    rows: list[tuple[str, str, list[re.Pattern[str]]]] = []
    for entry in load_cert_taxonomy():
        slug = str(entry.get("slug") or "").strip()
        display = str(entry.get("display_name") or slug).strip()
        if not slug:
            continue
        rows.append((slug, display, _patterns(entry)))
    return rows


def extract_certifications(title: str, description: str) -> list[dict[str, Any]]:
    """Return list of {slug, display_name, importance, evidence_span, extraction_method}."""
    text = f"{title or ''}\n{description or ''}"
    if not text.strip():
        return []
    found: dict[str, dict[str, Any]] = {}
    for slug, display, patterns in _compiled():
        for pat in patterns:
            m = pat.search(text)
            if not m:
                continue
            span = m.group(0)
            # Prefer "required" if near require/must/mandatory
            window = text[max(0, m.start() - 40) : m.end() + 40].lower()
            importance = (
                "required"
                if any(w in window for w in ("requir", "must have", "mandatory", "obbligator"))
                else "mentioned"
            )
            prev = found.get(slug)
            if prev and prev["importance"] == "required":
                break
            found[slug] = {
                "slug": slug,
                "display_name": display,
                "importance": importance,
                "evidence_span": span[:200],
                "extraction_method": "rules",
            }
            break
    return list(found.values())
