from __future__ import annotations

import re
from dataclasses import dataclass

RATE_PATTERN = re.compile(
    r"(?:(?P<currency>€|\$|£|EUR|USD|GBP|CHF)\s*)?(?P<amount>\d+(?:[.,]\d{1,2})?)"
    r"(?:\s*[-–to]+\s*(?P<amount_max>\d+(?:[.,]\d{1,2})?))?"
    r"(?:\s*(?P<currency2>EUR|USD|GBP|CHF|€|\$|£))?"
    r"(?:\s*/?\s*(?P<unit>hour|hr|h|day|daily|journée|giorno|month|year|annum))",
    re.IGNORECASE,
)

CURRENCY_MAP = {"€": "EUR", "$": "USD", "£": "GBP"}
UNIT_MAP = {
    "hour": "hour",
    "hr": "hour",
    "h": "hour",
    "day": "day",
    "daily": "day",
    "journée": "day",
    "giorno": "day",
    "month": "month",
    "year": "year",
    "annum": "year",
}


@dataclass
class ParsedRate:
    amount_min: float | None
    amount_max: float | None
    currency: str | None
    unit: str
    evidence_text: str
    confidence: float


def _to_float(raw: str | None) -> float | None:
    if not raw:
        return None
    return float(raw.replace(",", "."))


def parse_rate_text(text: str | None) -> ParsedRate | None:
    if not text:
        return None
    match = RATE_PATTERN.search(text)
    if not match:
        return None
    currency_token = match.group("currency") or match.group("currency2")
    if not currency_token:
        return None
    currency_raw = currency_token.upper()
    currency = CURRENCY_MAP.get(currency_token, currency_raw)
    unit_raw = (match.group("unit") or "").lower()
    unit = UNIT_MAP.get(unit_raw, "unknown")
    amount_min = _to_float(match.group("amount"))
    amount_max = _to_float(match.group("amount_max")) or amount_min
    return ParsedRate(
        amount_min=amount_min,
        amount_max=amount_max,
        currency=currency,
        unit=unit,
        evidence_text=match.group(0),
        confidence=0.7 if unit != "unknown" else 0.45,
    )
