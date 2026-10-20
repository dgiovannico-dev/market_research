from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.classification.taxonomy import build_alias_index
from app.normalization.rates import parse_rate_text

CONTRACT_PATTERNS = [
    (re.compile(r"\b(freelance|freelancer|partita\s*iva|p\.?\s*iva)\b", re.I), "freelance", 0.85),
    (re.compile(r"\b(b2b|contractor|contract\s+role|consultancy)\b", re.I), "b2b", 0.8),
    (re.compile(r"\b(temporary|fixed[\s-]?term|contratto\s+a\s+tempo)\b", re.I), "temporary", 0.75),
    (
        re.compile(r"\b(full[\s-]?time|permanent|employee|employment|unbefristet|cdi)\b", re.I),
        "employment",
        0.8,
    ),
]

REMOTE_PATTERNS = [
    (re.compile(r"\b(fully\s+remote|100%\s+remote|remote[\s-]?first|full remote)\b", re.I), "remote"),
    (re.compile(r"\bhybrid\b", re.I), "hybrid"),
    (re.compile(r"\b(on[\s-]?site|onsite|in[\s-]?office)\b", re.I), "onsite"),
]

SENIORITY_PATTERNS = [
    (re.compile(r"\b(principal|staff|lead|architect)\b", re.I), "senior"),
    (re.compile(r"\b(senior|sr\.?)\b", re.I), "senior"),
    (re.compile(r"\b(mid[\s-]?level|intermediate)\b", re.I), "mid"),
    (re.compile(r"\b(junior|jr\.?|entry[\s-]?level)\b", re.I), "junior"),
]

COUNTRY_HINTS = {
    "italy": "IT",
    "italia": "IT",
    "switzerland": "CH",
    "schweiz": "CH",
    "suisse": "CH",
    "zurich": "CH",
    "zürich": "CH",
    "germany": "DE",
    "deutschland": "DE",
    "berlin": "DE",
    "munich": "DE",
    "münchen": "DE",
    "austria": "AT",
    "vienna": "AT",
    "france": "FR",
    "paris": "FR",
    "netherlands": "NL",
    "amsterdam": "NL",
    "belgium": "BE",
    "luxembourg": "LU",
    "ireland": "IE",
    "dublin": "IE",
    "spain": "ES",
    "portugal": "PT",
    "united kingdom": "GB",
    "uk": "GB",
    "london": "GB",
    "united states": "US",
    "usa": "US",
    "worldwide": "WW",
    "anywhere": "WW",
}

RESIDENCE_RESTRICT = re.compile(
    r"\b(must\s+be\s+(located|based|resident)|only\s+(candidates|applicants)\s+in|"
    r"work\s+authorization|right\s+to\s+work|visa\s+sponsorship\s+not)\b",
    re.I,
)
RESIDENCE_ALLOW = re.compile(
    r"\b(worldwide|work\s+from\s+anywhere|candidates\s+from\s+any\s+country|"
    r"eu[\s/-]?wide|europe[\s-]?wide)\b",
    re.I,
)


@dataclass
class ClassificationResult:
    contract_type: str = "unknown"
    contract_type_confidence: float | None = None
    contract_evidence_kind: str = "inferred"
    remote_type: str = "unknown"
    seniority: str | None = None
    country_code: str = "unknown"
    residence_restriction: str = "unclear"
    b2b_eligible: bool | None = None
    b2b_evidence: str | None = None
    technologies: list[dict] = field(default_factory=list)
    rate: dict | None = None
    role_family: str | None = None
    classification_version: str = "rules-1.0.0"


def _detect_country(location: str | None, description: str | None) -> str:
    blob = f"{location or ''} {description or ''}".lower()
    for hint, code in COUNTRY_HINTS.items():
        if re.search(rf"\b{re.escape(hint)}\b", blob):
            return code
    return "unknown"


def _detect_role_family(title: str, description: str) -> str | None:
    blob = f"{title} {description}".lower()
    mapping = [
        ("platform engineer", "platform"),
        ("devops", "devops"),
        ("sre", "sre"),
        ("data engineer", "data_engineering"),
        ("mlops", "mlops"),
        ("machine learning", "ml"),
        ("llm", "ai_llm"),
        ("genai", "ai_llm"),
        ("rag", "ai_llm"),
        ("ai engineer", "ai_llm"),
        ("security", "security"),
        ("frontend", "frontend"),
        ("backend", "backend"),
        (r"full[\s-]?stack", "fullstack"),
        ("architect", "architecture"),
        ("cloud", "cloud"),
    ]
    for pattern, family in mapping:
        if re.search(pattern, blob):
            return family
    return None


def classify_job(
    *,
    title: str,
    description: str | None,
    location: str | None = None,
    salary_text: str | None = None,
    tags: list[str] | None = None,
    job_type: str | None = None,
) -> ClassificationResult:
    blob = " ".join(filter(None, [title, description or "", job_type or "", " ".join(tags or [])]))
    result = ClassificationResult()
    result.country_code = _detect_country(location, description)
    result.role_family = _detect_role_family(title, description or "")

    for pattern, value, conf in CONTRACT_PATTERNS:
        if pattern.search(blob):
            result.contract_type = value
            result.contract_type_confidence = conf
            result.contract_evidence_kind = "extracted"
            break

    if result.contract_type in {"freelance", "b2b", "contractor"}:
        result.b2b_eligible = True
        result.b2b_evidence = f"pattern match for {result.contract_type}"

    for pattern, value in REMOTE_PATTERNS:
        if pattern.search(blob) or (location and pattern.search(location)):
            result.remote_type = value
            break
    if result.remote_type == "unknown" and location and "remote" in location.lower():
        result.remote_type = "remote"

    for pattern, value in SENIORITY_PATTERNS:
        if pattern.search(blob):
            result.seniority = value
            break

    if RESIDENCE_RESTRICT.search(blob):
        result.residence_restriction = "explicitly_restricted"
    elif RESIDENCE_ALLOW.search(blob) or result.country_code == "WW":
        result.residence_restriction = "explicitly_allowed"

    alias_index = build_alias_index()
    found: dict[str, dict] = {}
    lower_blob = blob.lower()
    for alias, canonical in sorted(alias_index.items(), key=lambda x: -len(x[0])):
        if re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", lower_blob):
            found[canonical] = {
                "canonical_name": canonical,
                "importance": "mentioned",
                "extraction_method": "rules",
                "evidence_kind": "extracted",
                "confidence": 0.75,
                "evidence_span": alias,
            }
    # Title mentions → preferred weight
    title_l = title.lower()
    for canonical, item in found.items():
        if canonical.lower() in title_l:
            item["importance"] = "required"
            item["confidence"] = 0.85
    result.technologies = list(found.values())

    parsed = parse_rate_text(salary_text) or parse_rate_text(description)
    if parsed:
        result.rate = {
            "amount_min": parsed.amount_min,
            "amount_max": parsed.amount_max,
            "currency": parsed.currency,
            "unit": parsed.unit,
            "evidence_text": parsed.evidence_text,
            "confidence": parsed.confidence,
            "rate_type": "advertised",
            "extraction_method": "rules",
            "evidence_kind": "extracted",
        }
    return result
