#!/usr/bin/env python3
"""Generate docs/sources/ENDPOINT_PAGE_ANALYSIS.md from catalog + collectors.

Usage (repo root):
  python3 backend/scripts/generate_endpoint_page_analysis.py
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "data" / "sources" / "catalog.json"
COLLECTORS_DIR = ROOT / "backend" / "app" / "collectors"
OUT = ROOT / "docs" / "sources" / "ENDPOINT_PAGE_ANALYSIS.md"
ANALYSIS_DIR = ROOT / "docs" / "sources" / "analysis"

STATUS_ORDER = [
    "ACTIVE",
    "NEEDS_CREDENTIALS",
    "VALIDATED",
    "UNDER_REVIEW",
    "DISCOVERED",
    "REJECTED",
]

# Ignore attribution / docs noise when picking a primary endpoint
_SKIP_URL_SUBSTR = (
    "github.com/dgiovannico",
    "github.com/personio/api-docs",
    "localhost",
)

_CLASS_RE = re.compile(
    r"class\s+(\w+)\s*\([^)]*\):\s*\n(?P<body>(?:^[ \t]+.*\n|^$\n)+)",
    re.MULTILINE,
)
_ATTR_STR = re.compile(
    r"^\s+(source_key|base_url|collection_mode|name)\s*=\s*[\"']([^\"']+)[\"']",
    re.MULTILINE,
)
_CONST_URL = re.compile(
    r"^([A-Z][A-Z0-9_]*(?:URL|BASE|HOST|ENDPOINT|FEED|API)[A-Z0-9_]*)\s*=\s*[\"'](https?://[^\"']+)[\"']",
    re.MULTILINE,
)
_ANY_HTTPS = re.compile(r"https?://[^\s\"']+")


def _ok_url(u: str) -> bool:
    low = u.lower()
    return not any(s in low for s in _SKIP_URL_SUBSTR)


def scrape_collectors() -> dict[str, dict]:
    """Map source_key → {file, mode, primary, constants, urls}."""
    by_key: dict[str, dict] = {}
    for py in sorted(COLLECTORS_DIR.glob("*.py")):
        if py.name in ("base.py", "registry.py", "credentials.py", "__init__.py"):
            continue
        text = py.read_text(encoding="utf-8")
        module_consts = {k: v for k, v in _CONST_URL.findall(text) if _ok_url(v)}
        for m in _CLASS_RE.finditer(text):
            body = m.group("body")
            attrs = dict(_ATTR_STR.findall(body))
            sk = attrs.get("source_key")
            if not sk:
                continue
            urls = [u.rstrip(").,;") for u in _ANY_HTTPS.findall(body) if _ok_url(u)]
            primary = attrs.get("base_url") or ""
            if not primary or not _ok_url(primary):
                for _k, v in module_consts.items():
                    primary = v
                    break
            if not primary and urls:
                primary = urls[0]
            by_key[sk] = {
                "file": str(py.relative_to(ROOT)),
                "mode": attrs.get("collection_mode", "?"),
                "class": m.group(1),
                "primary": primary,
                "constants": module_consts,
                "urls": sorted(set(urls))[:12],
            }
    return by_key


def _sheet_analysis(ck: str | None) -> str | None:
    """Return Analysis value from docs/sources/analysis/{key}.md if present."""
    if not ck:
        return None
    path = ANALYSIS_DIR / f"{ck}.md"
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    m = re.search(r"\|\s*Analysis\s*\|\s*([^|]+)\|", text, re.IGNORECASE)
    if not m:
        return "PARTIAL"
    return m.group(1).strip()


def analysis_state(s: dict, collectors: dict) -> str:
    st = (s.get("verification_status") or "").upper()
    ck = s.get("connector_key")
    sheet = _sheet_analysis(ck)
    if sheet in ("DONE", "PARTIAL_SCAFFOLD", "PARTIAL"):
        return sheet
    if st == "ACTIVE" and ck in ("frankfurter", "ecb_fx", "manual_import"):
        return "N/A_HELPER"
    if st == "ACTIVE" and ck and ck in collectors:
        return "PARTIAL"
    if st == "ACTIVE" and ck:
        return "TODO"
    if st == "NEEDS_CREDENTIALS" and ck and ck in collectors:
        return "PARTIAL_SCAFFOLD"
    if st in ("REJECTED", "DISCOVERED"):
        return "SKIP"
    if st == "VALIDATED":
        return "TODO_REF"
    return "TODO"


def build_md(sources: list[dict], collectors: dict) -> str:
    today = date.today().isoformat()
    by_status: dict[str, list] = defaultdict(list)
    for s in sources:
        by_status[(s.get("verification_status") or "?").upper()].append(s)

    lines: list[str] = []
    a = lines.append

    a("# Source endpoint & page-structure analysis workbook")
    a("")
    a(
        "Working document for precise extraction: for **every** catalog source we "
        "record the HTTP endpoint (or feed/board URL), auth, response/page shape, "
        "and field mapping into `RawJob`."
    )
    a("")
    a("| | |")
    a("|---|---|")
    a(f"| Generated | {today} |")
    a("| Catalog | [`data/sources/catalog.json`](../../data/sources/catalog.json) |")
    a("| Collectors | `backend/app/collectors/*.py` |")
    a("| Regenerate | `python3 backend/scripts/generate_endpoint_page_analysis.py` |")
    a("| Live probe | [VALIDATION_REPORT.md](VALIDATION_REPORT.md) |")
    a(
        "| Detailed sheets | [`analysis/`](analysis/README.md) — one `{key}.md` per connector |"
    )
    a(
        "| Procedure | [SPEC-sources.md](../specs/SPEC-sources.md) · "
        "ADR-003 authorized connectors only |"
    )
    a("")
    a("## How to fill a source")
    a("")
    a(
        "Write/update `docs/sources/analysis/{connector_key}.md`, then re-run this "
        "generator so the tracker Analysis column reflects `| Analysis | DONE |`."
    )
    a("")
    a("For each entry, complete in order:")
    a("")
    a("1. **Endpoint** — method, URL template, auth, rate limits, pagination.")
    a(
        "2. **Payload / page structure** — top-level JSON keys or RSS/HTML selectors; "
        "one sample job item."
    )
    a(
        "3. **Field map** — source field → `RawJob` (`source_job_id`, `url`, `title`, "
        "`company`, `description`, `location`, `published_at`, `salary_text`, `tags`, "
        "`job_type`, `remote_hint`)."
    )
    a("4. **Evidence** — last successful probe date + `records_n`; thin vs standard.")
    a("5. Set **Analysis** to `DONE` only when 1–4 are verified (code + live or code-only for scaffolds).")
    a("")
    a(
        "Analysis: `TODO` · `PARTIAL` · `PARTIAL_SCAFFOLD` · `DONE` · `SKIP` · "
        "`N/A_HELPER` · `TODO_REF`."
    )
    a("")
    a("### Template")
    a("")
    a("```markdown")
    a("#### Endpoint")
    a("- Method / URL:")
    a("- Auth:")
    a("- Query / body:")
    a("- Pagination:")
    a("- Rate limit / ToS:")
    a("")
    a("#### Payload / page structure")
    a("- Content-Type:")
    a("- Path to job list:")
    a("- Per-item schema:")
    a("- Sample (redacted) item:")
    a("")
    a("#### Field map → RawJob")
    a("| Source field | RawJob | Notes |")
    a("|--------------|--------|-------|")
    a("| | source_job_id | |")
    a("| | url | |")
    a("| | title | |")
    a("| | company | |")
    a("| | description | |")
    a("| | location | |")
    a("| | published_at | |")
    a("| | salary_text | |")
    a("| | tags | |")
    a("")
    a("#### Gaps / precision risks")
    a("- ")
    a("```")
    a("")
    a("## Tracker (all sources)")
    a("")
    a(
        "| ID | Key | Name | Status | Cat | Analysis | Primary endpoint "
        "(from code/catalog) |"
    )
    a("|----|-----|------|--------|-----|----------|--------------------------------------|")

    for st in STATUS_ORDER:
        for s in sorted(by_status.get(st, []), key=lambda x: x["catalog_id"]):
            ck = s.get("connector_key") or ""
            meta = collectors.get(ck) or {}
            primary = meta.get("primary") or s.get("docs_url") or s.get("official_url") or ""
            primary = primary.replace("|", "\\|")[:90]
            name = (s.get("name") or "").replace("|", "\\|")
            a(
                f"| {s['catalog_id']} | `{ck or '—'}` | {name} | {st} | "
                f"{s.get('category') or '—'} | {analysis_state(s, collectors)} | "
                f"{primary or '—'} |"
            )

    an = Counter(analysis_state(s, collectors) for s in sources)
    a("")
    a(
        "**Analysis progress:** "
        + ", ".join(f"`{k}`={v}" for k, v in sorted(an.items()))
    )
    a("")
    a("---")
    a("")
    a("## Detail sheets — ACTIVE")
    a("")
    a(
        "Endpoint pre-filled from collector `base_url` / constants. "
        "Full payload + field maps live in [`analysis/`](analysis/) when Analysis=`DONE`."
    )
    a("")

    for s in sorted(
        by_status.get("ACTIVE", []),
        key=lambda x: (x.get("connector_key") or "", x["catalog_id"]),
    ):
        _detail_active(a, s, collectors)

    a("## Detail sheets — NEEDS_CREDENTIALS (scaffolds)")
    a("")
    cred = [
        s
        for s in by_status.get("NEEDS_CREDENTIALS", [])
        if s.get("connector_key") in collectors
    ]
    for s in sorted(cred, key=lambda x: x.get("connector_key") or ""):
        _detail_scaffold(a, s, collectors)

    a("## Detail sheets — VALIDATED (reference / non-job)")
    a("")
    for s in sorted(by_status.get("VALIDATED", []), key=lambda x: x["catalog_id"]):
        a(f"### {s['name']} (catalog_id={s['catalog_id']})")
        a(f"- **URL:** {s.get('docs_url') or s.get('official_url') or '—'}")
        a(
            "- **Role:** reference/taxonomy/stats — not job ingest. "
            "**Analysis:** TODO_REF if product needs the response schema."
        )
        a(f"- **Notes:** {s.get('notes') or '—'}")
        a("")

    a("## Detail sheets — NEEDS_CREDENTIALS without connector")
    a("")
    a(
        "No in-repo collector. Fill only when an authorized API/partner path exists "
        "(ADR-003)."
    )
    a("")
    for s in sorted(
        [x for x in by_status.get("NEEDS_CREDENTIALS", []) if not x.get("connector_key")],
        key=lambda x: x["catalog_id"],
    ):
        _detail_stub(a, s)

    a("## Detail sheets — UNDER_REVIEW")
    a("")
    a(
        "Candidates without a wired connector. Prioritize by GEO/role needs before "
        "deep HTML analysis."
    )
    a("")
    for s in sorted(by_status.get("UNDER_REVIEW", []), key=lambda x: x["catalog_id"]):
        _detail_stub(a, s)

    a("## DISCOVERED / REJECTED")
    a("")
    for s in sorted(
        by_status.get("DISCOVERED", []) + by_status.get("REJECTED", []),
        key=lambda x: x["catalog_id"],
    ):
        a(
            f"- **{s['name']}** (id={s['catalog_id']}, `{s.get('verification_status')}`) — "
            f"Analysis: SKIP. dup_of={s.get('duplicate_of')} · {s.get('notes') or ''}"
        )
    a("")
    return "\n".join(lines) + "\n"


def _detail_active(a, s: dict, collectors: dict) -> None:
    ck = s.get("connector_key") or "—"
    meta = collectors.get(ck) if ck != "—" else None
    meta = meta or {}
    primary = meta.get("primary") or s.get("docs_url") or s.get("official_url") or "—"
    a(f"### {s['name']} (`{ck}`)")
    a("")
    a(
        f"- **Catalog ID:** {s['catalog_id']} · **Category:** {s.get('category')} · "
        f"**Access:** {s.get('access_mode')}"
    )
    a(f"- **Verification:** ACTIVE · **Analysis:** {analysis_state(s, collectors)}")
    if meta:
        a(
            f"- **Collector:** `{meta.get('file')}` · **class:** `{meta.get('class')}` · "
            f"**collection_mode:** `{meta.get('mode', '?')}`"
        )
    a(
        f"- **Official:** {s.get('official_url') or '—'} · "
        f"**Docs:** {s.get('docs_url') or '—'}"
    )
    if s.get("notes"):
        a(f"- **Catalog notes:** {s['notes']}")
    sheet = ANALYSIS_DIR / f"{ck}.md" if ck != "—" else None
    if sheet and sheet.is_file():
        a(f"- **Detailed analysis:** [`analysis/{ck}.md`](analysis/{ck}.md)")
    else:
        a(f"- **Detailed analysis:** _(create `analysis/{ck}.md`)_")
    a("")
    a("#### Endpoint")
    a(f"- **Primary URL:** `{primary}`")
    consts = meta.get("constants") or {}
    if consts:
        a("- **Named constants:**")
        for k, v in consts.items():
            a(f"  - `{k}` = `{v}`")
    urls = meta.get("urls") or []
    extras = [u for u in urls if u != primary][:6]
    if extras:
        a("- **Other URLs in collector:**")
        for u in extras:
            a(f"  - `{u}`")
    if sheet and sheet.is_file():
        a("- See detailed sheet for method/auth/pagination, payload, field map, gaps.")
    else:
        a("- **Method / auth / pagination:** _(fill in analysis sheet)_")
        a("- **Payload / field map:** _(fill in analysis sheet)_")
    a("")
    a("---")
    a("")


def _detail_scaffold(a, s: dict, collectors: dict) -> None:
    ck = s["connector_key"]
    meta = collectors.get(ck) or {}
    primary = meta.get("primary") or s.get("docs_url") or "—"
    a(f"### {s['name']} (`{ck}`)")
    a("")
    a(
        f"- **Catalog ID:** {s['catalog_id']} · **Analysis:** PARTIAL_SCAFFOLD · "
        f"**Mode:** `{meta.get('mode', '?')}`"
    )
    a(f"- **Collector:** `{meta.get('file', '—')}` · **class:** `{meta.get('class', '—')}`")
    a(f"- **Primary URL:** `{primary}`")
    for k, v in (meta.get("constants") or {}).items():
        a(f"  - `{k}` = `{v}`")
    a(
        "- **Credentials:** required (fail-closed). See "
        "[CREDENTIALED_CONNECTORS.md](CREDENTIALED_CONNECTORS.md)."
    )
    sheet = ANALYSIS_DIR / f"{ck}.md"
    if sheet.is_file():
        a(f"- **Detailed analysis:** [`analysis/{ck}.md`](analysis/{ck}.md)")
    else:
        a("- **Payload / field map:** _(fill `analysis/{key}.md` from code; live after keys)_")
    a("")
    a("---")
    a("")


def _detail_stub(a, s: dict) -> None:
    a(f"### {s['name']} (id={s['catalog_id']}, cat={s.get('category')})")
    a(
        f"- **Official:** {s.get('official_url') or '—'} · "
        f"**Docs:** {s.get('docs_url') or '—'}"
    )
    a(f"- **Access mode:** {s.get('access_mode') or '—'} · **Analysis:** TODO")
    a(f"- **Notes:** {s.get('notes') or '—'}")
    a("- **Endpoint / payload / field map:** _(not started)_")
    a("")


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    sources = catalog["sources"]
    collectors = scrape_collectors()
    text = build_md(sources, collectors)
    OUT.write_text(text, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(text)} bytes, {len(sources)} sources, {len(collectors)} collectors)")


if __name__ == "__main__":
    main()
