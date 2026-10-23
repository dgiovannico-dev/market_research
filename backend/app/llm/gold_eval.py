"""Gold-label evaluation against the rules classifier."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.classification.rules import classify_job

_GOLD_PATH = Path(__file__).resolve().parents[3] / "data" / "eval" / "gold_labels.json"


def load_gold_labels(path: Path | None = None) -> dict[str, Any]:
    p = path or _GOLD_PATH
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def evaluate_gold_labels(path: Path | None = None) -> dict[str, Any]:
    payload = load_gold_labels(path)
    items = payload.get("items") or []
    fields = ("contract_type", "remote_type")
    matches = {f: 0 for f in fields}
    compared = 0
    details: list[dict[str, Any]] = []

    for item in items:
        expected = item.get("expected") or {}
        fresh = classify_job(
            title=item.get("title") or "",
            description=item.get("description"),
            location=item.get("location"),
        )
        compared += 1
        row: dict[str, Any] = {"id": item.get("id"), "ok": True, "fields": {}}
        for field in fields:
            exp = expected.get(field)
            if exp is None:
                continue
            pred = getattr(fresh, field, None)
            hit = exp == pred
            if hit:
                matches[field] += 1
            else:
                row["ok"] = False
            row["fields"][field] = {"expected": exp, "predicted": pred, "match": hit}
        details.append(row)

    field_n = {f: sum(1 for i in items if (i.get("expected") or {}).get(f) is not None) for f in fields}
    accuracy = {
        f: round(matches[f] / field_n[f], 3) if field_n[f] else None for f in fields
    }
    scored = sum(field_n.values())
    overall = round(sum(matches.values()) / scored, 3) if scored else None

    return {
        "method": "gold_labels_rules",
        "evidence_kind": "manually_verified",
        "dataset_version": payload.get("version"),
        "items_evaluated": compared,
        "field_accuracy": accuracy,
        "overall_accuracy": overall,
        "details": details,
        "limits": (
            "Small curated gold set for classifier regression only. "
            "Accuracy is not market demand. Expand data/eval/gold_labels.json carefully."
        ),
        "dataset_path": str(_GOLD_PATH),
    }
