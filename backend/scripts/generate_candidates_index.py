#!/usr/bin/env python3
"""Regenerate docs/sources/analysis/candidates/INDEX.md from sheet front-matter."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "sources" / "analysis" / "candidates"

_ORDER = {
    "IMPLEMENTED": 0,
    "DOCUMENTED": 1,
    "PARTNER_ONLY": 2,
    "TODO_ACCESS": 3,
    "BLOCKED_TOS": 4,
    "?": 9,
}


def _norm_analysis(an: str) -> str:
    a = an.strip()
    if "implemented" in a.lower() or a.upper().startswith("IMPLEMENTED"):
        return "IMPLEMENTED"
    for sep in (" →", " —", " - ", " ("):
        if sep in a:
            a = a.split(sep, 1)[0].strip()
    return a


def main() -> None:
    rows: list[tuple[str, str, str, str]] = []
    for p in sorted(OUT.glob("*.md")):
        if p.name in ("README.md", "INDEX.md"):
            continue
        t = p.read_text(encoding="utf-8")
        title = t.splitlines()[0].lstrip("# ").strip()
        an = re.search(r"\|\s*Analysis\s*\|\s*([^|]+)\|", t)
        cat = re.search(r"\|\s*Category\s*\|\s*([^|]+)\|", t)
        rows.append(
            (
                _norm_analysis(an.group(1) if an else "?"),
                p.name,
                title,
                (cat.group(1).strip() if cat else "?"),
            )
        )
    lines = [
        "# Candidate source analysis index",
        "",
        f"{len(rows)} sheets (catalog entries without wired connector analysis).",
        "Connectors with live maps: [`../INDEX.md`](../INDEX.md).",
        "",
        f"**By Analysis:** {dict(Counter(r[0] for r in rows))}",
        "",
        "| Analysis | File | Title | Cat |",
        "|----------|------|-------|-----|",
    ]
    for an, name, title, cat in sorted(rows, key=lambda r: (_ORDER.get(r[0], 5), r[1])):
        lines.append(f"| {an} | [`{name}`]({name}) | {title} | {cat} |")
    lines.append("")
    (OUT / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT / 'INDEX.md'} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
