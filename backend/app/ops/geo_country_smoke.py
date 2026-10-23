"""Geo connector country_code DSS smoke helpers (pure; no DB).

Uses ``GET /api/v1/market/quality?lens=all`` ``by_source`` rows to assert that
ISO-tagged geo connectors keep a high share of known ``Job.country_code``.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Iterable, Literal, Mapping, Sequence

# Primary ISO tags for Plan D geo connectors (okemprego may also emit BR/AO).
GEO_TAGGED_CONNECTORS: dict[str, frozenset[str]] = {
    "okemprego": frozenset({"PT", "BR", "AO"}),
    "jobbank_ca": frozenset({"CA"}),
    "viewjobs": frozenset({"AU"}),
    "devglobaljobs": frozenset({"LU", "BG"}),
}

DEFAULT_MIN_KNOWN_PCT = 95.0

VerdictStatus = Literal["PASS", "FAIL", "SKIP"]


@dataclass(frozen=True)
class SourceVerdict:
    connector_type: str
    status: VerdictStatus
    n: int
    pct_known_country: float | None
    detail: str
    expected_tags: frozenset[str]


def aggregate_known_by_connector(
    by_source: Sequence[Mapping[str, Any]],
) -> dict[str, tuple[int, float]]:
    """Sum jobs per ``connector_type`` and compute weighted known-country %."""
    totals: dict[str, list[float]] = {}  # connector -> [n_sum, known_sum]
    for row in by_source:
        key = row.get("connector_type")
        if not key:
            continue
        n = int(row.get("n") or 0)
        if n <= 0:
            continue
        pct = float(row.get("pct_known_country") or 0.0)
        bucket = totals.setdefault(str(key), [0.0, 0.0])
        bucket[0] += n
        bucket[1] += n * (pct / 100.0)
    out: dict[str, tuple[int, float]] = {}
    for key, (n_sum, known_sum) in totals.items():
        n_i = int(n_sum)
        pct = round((known_sum / n_sum) * 100.0, 2) if n_sum else 0.0
        out[key] = (n_i, pct)
    return out


def evaluate_geo_country(
    by_source: Sequence[Mapping[str, Any]],
    *,
    connectors: Iterable[str] | None = None,
    min_known_pct: float = DEFAULT_MIN_KNOWN_PCT,
) -> list[SourceVerdict]:
    """Return PASS/FAIL/SKIP per geo connector from quality ``by_source`` rows.

    - SKIP when no jobs for that connector (honest empty / not yet crawled).
    - FAIL when jobs exist and known-country share is below ``min_known_pct``.
    - PASS otherwise.
    """
    wanted = list(connectors) if connectors is not None else list(GEO_TAGGED_CONNECTORS)
    agg = aggregate_known_by_connector(by_source)
    verdicts: list[SourceVerdict] = []
    for ctype in wanted:
        tags = GEO_TAGGED_CONNECTORS.get(ctype, frozenset())
        n, pct = agg.get(ctype, (0, 0.0))
        if n <= 0:
            verdicts.append(
                SourceVerdict(
                    connector_type=ctype,
                    status="SKIP",
                    n=0,
                    pct_known_country=None,
                    detail="no jobs for connector (soft skip)",
                    expected_tags=tags,
                )
            )
            continue
        if pct + 1e-9 < min_known_pct:
            verdicts.append(
                SourceVerdict(
                    connector_type=ctype,
                    status="FAIL",
                    n=n,
                    pct_known_country=pct,
                    detail=(
                        f"known country {pct}% < {min_known_pct}% "
                        f"(expected tags {sorted(tags) or 'n/a'})"
                    ),
                    expected_tags=tags,
                )
            )
            continue
        verdicts.append(
            SourceVerdict(
                connector_type=ctype,
                status="PASS",
                n=n,
                pct_known_country=pct,
                detail=(
                    f"known country {pct}% ≥ {min_known_pct}% "
                    f"(expected tags {sorted(tags) or 'n/a'})"
                ),
                expected_tags=tags,
            )
        )
    return verdicts


def exit_code_for_verdicts(verdicts: Sequence[SourceVerdict]) -> int:
    """0 if every present source passed or all skipped; 1 on any FAIL."""
    return 1 if any(v.status == "FAIL" for v in verdicts) else 0


def format_verdict_lines(verdicts: Sequence[SourceVerdict]) -> list[str]:
    lines: list[str] = []
    for v in verdicts:
        pct = "n/a" if v.pct_known_country is None else f"{v.pct_known_country}%"
        lines.append(
            f"smoke_geo_country {v.status}: {v.connector_type} "
            f"n={v.n} known={pct} — {v.detail}"
        )
    return lines


def _load_quality_payload(api_url: str | None, stdin_json: bool) -> dict[str, Any]:
    if stdin_json or not api_url:
        raw = sys.stdin.read()
        if not raw.strip():
            raise SystemExit("smoke_geo_country: empty stdin (expected quality JSON)")
        return json.loads(raw)
    url = api_url.rstrip("/") + "/api/v1/market/quality?lens=all"
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise SystemExit(f"smoke_geo_country FAIL: GET {url}: {exc}") from exc


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Assert geo connector Job.country_code known share (DSS smoke)."
    )
    parser.add_argument(
        "--api-url",
        default=None,
        help="Base API URL (fetches /api/v1/market/quality?lens=all). "
        "Omit to read quality JSON from stdin.",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read quality JSON from stdin (default when --api-url omitted).",
    )
    parser.add_argument(
        "--min-known-pct",
        type=float,
        default=DEFAULT_MIN_KNOWN_PCT,
        help=f"Minimum known-country %% (default {DEFAULT_MIN_KNOWN_PCT})",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    payload = _load_quality_payload(args.api_url, stdin_json=args.stdin or not args.api_url)
    by_source = payload.get("by_source") or []
    if not isinstance(by_source, list):
        print("smoke_geo_country FAIL: by_source missing or not a list", file=sys.stderr)
        return 1

    verdicts = evaluate_geo_country(by_source, min_known_pct=args.min_known_pct)
    for line in format_verdict_lines(verdicts):
        print(line)

    code = exit_code_for_verdicts(verdicts)
    present = sum(1 for v in verdicts if v.status != "SKIP")
    skipped = sum(1 for v in verdicts if v.status == "SKIP")
    failed = sum(1 for v in verdicts if v.status == "FAIL")
    label = "OK" if code == 0 else "FAIL"
    print(
        f"smoke_geo_country {label}: present={present} skipped={skipped} failed={failed}"
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
