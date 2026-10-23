from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.classification.taxonomy import TAXONOMY
from app.collectors.credentials import has_credentials
from app.collectors.registry import COLLECTORS, CREDENTIALED_SCAFFOLDS
from app.sources.catalog import load_catalog
from app.storage.models import SearchQuery, Source, Technology, UserProfile, UserSkill

_FOCUS_COUNTRIES = ["IT", "CH", "DE", "AT", "FR", "NL", "BE", "LU", "IE", "ES", "GB", "US"]
_FOCUS_CONTRACT_TYPES = ["freelance", "b2b", "contractor"]
# Persona-aligned focus probes (Demand Compass "My focus" starters).
# Naming: distinctive tech/role tokens first so rematch signal tokens stay sharp.
_FOCUS_STARTERS = [
    # Java / JVM backend
    ("Senior Java Contractor", "Senior Java Contractor"),
    ("Java Spring Boot B2B", "Java Spring Boot B2B"),
    ("Kotlin Backend B2B", "Kotlin Backend B2B"),
    # Python / Node / other backends
    ("Senior Python Contractor", "Senior Python Contractor"),
    ("FastAPI Backend B2B", "FastAPI Backend B2B"),
    ("Node.js Backend Freelance", "Node.js Backend Freelance"),
    ("Go Backend Contractor", "Go Backend Contractor"),
    ("Dotnet C# Contractor B2B", "Dotnet C# Contractor B2B"),
    # Full-stack / frontend
    ("Fullstack Engineer Freelance", "Fullstack Engineer Freelance"),
    ("React Frontend B2B", "React Frontend B2B"),
    ("TypeScript Fullstack Contractor", "TypeScript Fullstack Contractor"),
    # Cloud / platform / DevOps
    ("Cloud Architect Freelance", "Cloud Architect Freelance"),
    ("Kubernetes Consultant", "Kubernetes Consultant"),
    ("DevOps Engineer B2B", "DevOps Engineer B2B"),
    ("Platform Engineer Freelance", "Platform Engineer Freelance"),
    ("SRE Consultant", "SRE Consultant"),
    ("AWS Cloud Engineer B2B", "AWS Cloud Engineer B2B"),
    ("Terraform Infrastructure Freelance", "Terraform Infrastructure Freelance"),
    # Architecture / leadership
    ("Solution Architect B2B", "Solution Architect B2B"),
    ("Software Architect Freelance", "Software Architect Freelance"),
    ("Enterprise Architect Consultant", "Enterprise Architect Consultant"),
    # AI / LLM / RAG / agents
    ("AI Engineer B2B", "AI Engineer B2B"),
    ("LLM Engineer Freelance", "LLM Engineer Freelance"),
    ("RAG Engineer", "RAG Engineer"),
    ("MLOps Engineer", "MLOps Engineer"),
    ("AI Agent Engineer B2B", "AI Agent Engineer B2B"),
    ("Generative AI Architect Freelance", "Generative AI Architect Freelance"),
    ("AI Platform Engineer B2B", "AI Platform Engineer B2B"),
    # Data / ML
    ("Data Engineer Freelance", "Data Engineer Freelance"),
    ("Machine Learning Engineer B2B", "Machine Learning Engineer B2B"),
    ("Analytics Engineer Contractor", "Analytics Engineer Contractor"),
    # Security
    ("Security Engineer B2B", "Security Engineer B2B"),
    ("Cybersecurity Consultant", "Cybersecurity Consultant"),
    ("DevSecOps Engineer Freelance", "DevSecOps Engineer Freelance"),
]

# Old seed labels replaced by clearer rematch-friendly names.
_SUPERSEDED_FOCUS_NAMES = {
    ".NET Contractor B2B": "Dotnet C# Contractor B2B",
    "Full-Stack Engineer Freelance": "Fullstack Engineer Freelance",
    "TypeScript Full-Stack Contractor": "TypeScript Fullstack Contractor",
}


def _discovery_watchlist_path() -> Path | None:
    """Resolve discovery_watchlist.json relative to repo root or CWD."""
    here = Path(__file__).resolve()
    candidates = [
        here.parents[3] / "data" / "research" / "discovery_watchlist.json",
        Path.cwd() / "data" / "research" / "discovery_watchlist.json",
        Path.cwd().parent / "data" / "research" / "discovery_watchlist.json",
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None


_STATUS_TO_CONNECTOR = {
    "ACTIVE": "enabled",
    "VALIDATED": "unsupported",
    "NEEDS_CREDENTIALS": "requires_credentials",
    "PENDING_ACCESS": "requires_credentials",
    "BLOCKED": "unsupported",
    "REJECTED": "unsupported",
    "DEPRECATED": "unsupported",
    "DISCOVERED": "unsupported",
    "UNDER_REVIEW": "unsupported",
    "DEGRADED": "enabled",
    "IMPLEMENTED": "enabled",
}

# Test / fixture rows that must never stay runnable in seeded DBs.
_NOISE_SOURCE_NAME = re.compile(
    r"^(bf_src_|dedup_empty_url_|manual_empty|clip-emp-)",
    re.IGNORECASE,
)
# Orphan connector_types with no COLLECTORS entry and no lawful public path.
_DEAD_ORPHAN_CONNECTORS = frozenset({"freework", "freelancermap", "test", "fixture"})


def _retire_noise_sources(db: Session) -> None:
    """Disable accidental test sources and demoted stubs left enabled."""
    for row in db.scalars(select(Source)).all():
        ctype = row.connector_type or ""
        name = row.name or ""
        if ctype.startswith("dup_"):
            row.enabled = False
            row.connector_status = "unsupported"
            continue
        if _NOISE_SOURCE_NAME.match(name) or ctype in _DEAD_ORPHAN_CONNECTORS:
            row.enabled = False
            row.connector_status = "unsupported"
            row.verification_status = "REJECTED"
            row.coverage_notes = row.coverage_notes or (
                "Retired: no lawful public job connector for this key."
            )


_NON_JOB_CATALOG_CATEGORIES = frozenset({"E", "F", "G", "H", "I"})


def _sync_catalog_sources(db: Session) -> None:
    catalog = load_catalog()
    for item in catalog.get("sources") or []:
        name = item["name"]
        key = item.get("connector_key") or f"catalog_{item['catalog_id']}"
        # Catalog duplicates: keep a disabled stub if already in DB; do not create new rows.
        if item.get("duplicate_of"):
            existing = db.scalar(select(Source).where(Source.catalog_id == item["catalog_id"]))
            if not existing:
                existing = db.scalar(select(Source).where(Source.name == name))
            if existing:
                existing.catalog_id = item["catalog_id"]
                existing.category = item.get("category")
                existing.enabled = False
                existing.connector_status = "disabled"
                existing.verification_status = "REJECTED"
                existing.coverage_notes = item.get("notes") or existing.coverage_notes
            continue
        vstatus = item.get("verification_status") or "DISCOVERED"
        connector_status = _STATUS_TO_CONNECTOR.get(vstatus, "unsupported")
        runnable = key in COLLECTORS and vstatus in {"ACTIVE", "IMPLEMENTED", "DEGRADED"}
        # Credentialed scaffolds: runnable when keys set, but keep catalog NEEDS_CREDENTIALS until live ACTIVE
        if key in CREDENTIALED_SCAFFOLDS and key in COLLECTORS:
            runnable = has_credentials(key)
            if runnable:
                connector_status = "enabled"
            # never promote verification_status to ACTIVE from keys alone
        elif (
            key
            in {
                "ashby",
                "greenhouse",
                "lever",
                "smartrecruiters",
                "personio",
                "teamtailor",
                "recruitee",
                "pinpoint",
                "workable",
                "workday",
                "bamboohr",
            }
            and key in COLLECTORS
        ):
            if not has_credentials(key):
                runnable = False
        if key == "manual_import":
            connector_status = "manual_import"
            runnable = False
        # Non-job catalog rows (stats, reports, FX, taxonomy, procurement, discovery).
        # Keep them out of unsupported so Quality defaults stay job-ops focused.
        elif key in {"frankfurter", "ecb_fx"} or (
            item.get("category") in _NON_JOB_CATALOG_CATEGORIES and key not in COLLECTORS
        ):
            runnable = False
            connector_status = "disabled"

        existing = db.scalar(select(Source).where(Source.catalog_id == item["catalog_id"]))
        if not existing:
            existing = db.scalar(select(Source).where(Source.name == name))
        now = datetime.now(timezone.utc)
        if existing:
            existing.verification_status = vstatus
            existing.catalog_id = item["catalog_id"]
            existing.category = item.get("category")
            existing.access_mode = item.get("access_mode")
            existing.coverage_notes = item.get("notes")
            existing.docs_url = item.get("docs_url")
            existing.base_url = item.get("official_url")
            existing.connector_type = key
            existing.connector_status = "enabled" if runnable else connector_status
            existing.enabled = runnable or key == "manual_import"
            if vstatus in {"ACTIVE", "VALIDATED"}:
                existing.last_validated_at = now
            continue

        db.add(
            Source(
                name=name,
                source_type="api" if runnable else "external",
                base_url=item.get("official_url"),
                connector_type=key,
                enabled=runnable or key == "manual_import",
                connector_status="enabled" if runnable else connector_status,
                verification_status=vstatus,
                catalog_id=item["catalog_id"],
                category=item.get("category"),
                access_mode=item.get("access_mode"),
                configuration={},
                coverage_notes=item.get("notes"),
                coverage_geography="Worldwide (source-biased)" if runnable else None,
                docs_url=item.get("docs_url"),
                last_validated_at=now if vstatus in {"ACTIVE", "VALIDATED"} else None,
            )
        )


def seed_reference_data(db: Session) -> None:
    # Ensure runnable collectors exist even if catalog missing a row
    for key, collector in COLLECTORS.items():
        can_run = has_credentials(key)
        # Public ACTIVE connectors stay runnable; credentialed scaffolds need keys
        # Ashby is public per-org (like Greenhouse): ACTIVE when ASHBY_ORGS set; else VALIDATED.
        default_vstatus = (
            "ACTIVE" if key not in CREDENTIALED_SCAFFOLDS else "NEEDS_CREDENTIALS"
        )
        if key == "ashby":
            default_vstatus = "ACTIVE" if can_run else "VALIDATED"
        existing = db.scalar(select(Source).where(Source.connector_type == key))
        if existing:
            existing.enabled = can_run
            existing.connector_status = "enabled" if can_run else "requires_credentials"
            if existing.verification_status != "ACTIVE":
                existing.verification_status = existing.verification_status or default_vstatus
            continue
        by_name = db.scalar(select(Source).where(Source.name == collector.name))
        if by_name:
            by_name.connector_type = key
            by_name.enabled = can_run
            by_name.connector_status = "enabled" if can_run else "requires_credentials"
            if by_name.verification_status != "ACTIVE":
                by_name.verification_status = default_vstatus
            continue
        db.add(
            Source(
                name=collector.name,
                source_type="api",
                base_url=getattr(collector, "base_url", None),
                connector_type=key,
                enabled=can_run,
                connector_status="enabled" if can_run else "requires_credentials",
                verification_status=default_vstatus,
                configuration={},
                coverage_notes="Public connector registered in COLLECTORS.",
                docs_url=getattr(collector, "base_url", None),
            )
        )
    db.flush()

    _sync_catalog_sources(db)

    # Prefer a single DB row per connector_type (catalog name wins over stub)
    for key in COLLECTORS:
        rows = list(db.scalars(select(Source).where(Source.connector_type == key)).all())
        if len(rows) <= 1:
            continue
        primary = next((r for r in rows if r.catalog_id is not None), rows[0])
        for r in rows:
            if r.id == primary.id:
                continue
            # Demote duplicate stub names so UI stays clean
            r.connector_type = f"dup_{key}_{r.id}"
            r.enabled = False
            r.connector_status = "unsupported"
            r.verification_status = "REJECTED"
            r.coverage_notes = (
                f"Demoted duplicate stub of connector `{key}` "
                f"(canonical row id={primary.id}). Hidden from /sources list."
            )

    _retire_noise_sources(db)

    for tech in TAXONOMY:
        if db.scalar(select(Technology).where(Technology.canonical_name == tech["canonical_name"])):
            continue
        db.add(
            Technology(
                canonical_name=tech["canonical_name"],
                category=tech["category"],
                aliases=tech.get("aliases", []),
            )
        )

    _seed_focus_starters(db)
    _seed_discovery_watchlist(db)

    profile = db.scalar(select(UserProfile).limit(1))
    if not profile:
        profile = UserProfile(
            display_name="Default IT Freelance",
            years_experience=10,
            residence_country="IT",
            languages=["it", "en"],
            remote_preference="remote",
            min_rate_amount=500,
            target_rate_amount=650,
            rate_unit="day",
            rate_currency="EUR",
        )
        db.add(profile)
        db.flush()

    if not db.scalar(select(UserSkill).where(UserSkill.profile_id == profile.id).limit(1)):
        for name in ("Java", "Spring Boot", "Kubernetes", "Python", "PostgreSQL"):
            tech = db.scalar(select(Technology).where(Technology.canonical_name == name))
            if tech:
                db.add(
                    UserSkill(
                        profile_id=profile.id,
                        technology_id=tech.id,
                        level="advanced",
                        years=5,
                        verifiable=True,
                    )
                )

    db.commit()


def _seed_focus_starters(db: Session) -> None:
    for old_name, new_name in _SUPERSEDED_FOCUS_NAMES.items():
        legacy = db.scalar(select(SearchQuery).where(SearchQuery.name == old_name))
        if legacy and legacy.origin == "seed_focus" and legacy.kind == "focus":
            # Prefer the replacement row when both exist; otherwise rename in place.
            replacement = db.scalar(select(SearchQuery).where(SearchQuery.name == new_name))
            if replacement is not None:
                legacy.enabled = False
            else:
                legacy.name = new_name
                legacy.query_text = new_name

    for name, text in _FOCUS_STARTERS:
        existing = db.scalar(select(SearchQuery).where(SearchQuery.name == name))
        if existing:
            # Do not re-tag discovery intents that share a label by coincidence.
            if existing.kind == "discovery":
                continue
            existing.kind = "focus"
            if existing.origin in {None, "", "user"}:
                existing.origin = "seed_focus"
            existing.schedule_hint = existing.schedule_hint or "daily"
            existing.enabled = True
            existing.countries = list(_FOCUS_COUNTRIES)
            existing.contract_types = list(_FOCUS_CONTRACT_TYPES)
            continue
        db.add(
            SearchQuery(
                name=name,
                query_text=text,
                countries=list(_FOCUS_COUNTRIES),
                role_families=[],
                contract_types=list(_FOCUS_CONTRACT_TYPES),
                kind="focus",
                origin="seed_focus",
                schedule_hint="daily",
                enabled=True,
            )
        )


def _seed_discovery_watchlist(db: Session) -> None:
    path = _discovery_watchlist_path()
    if path is None:
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    for item in payload.get("intents") or []:
        label = item.get("label") or item.get("name")
        text = item.get("query_text") or ""
        if not label or not text:
            continue
        exists = db.scalar(
            select(SearchQuery).where(
                SearchQuery.kind == "discovery",
                SearchQuery.name == label,
                SearchQuery.deleted_at.is_(None),
            )
        )
        if exists:
            exists.query_text = text
            exists.origin = "seed_discovery"
            exists.schedule_hint = exists.schedule_hint or "daily"
            filters = item.get("filters")
            if isinstance(filters, dict):
                exists.filters_extra = filters or None
            continue
        filters = item.get("filters") if isinstance(item.get("filters"), dict) else {}
        db.add(
            SearchQuery(
                name=label,
                query_text=text,
                countries=list((filters or {}).get("countries") or []),
                role_families=[],
                contract_types=[],
                filters_extra=filters or None,
                kind="discovery",
                origin="seed_discovery",
                schedule_hint="daily",
                enabled=True,
            )
        )
