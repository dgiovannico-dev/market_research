from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.classification.taxonomy import TAXONOMY
from app.collectors.registry import COLLECTORS, UNSUPPORTED_SOURCES
from app.storage.models import SearchQuery, Source, Technology, UserProfile, UserSkill


def seed_reference_data(db: Session) -> None:
    for key, collector in COLLECTORS.items():
        existing = db.scalar(select(Source).where(Source.name == collector.name))
        if existing:
            continue
        db.add(
            Source(
                name=collector.name,
                source_type="api",
                base_url=getattr(collector, "base_url", None),
                connector_type=key,
                enabled=True,
                connector_status="enabled",
                configuration={},
                coverage_notes="Public job board API. Coverage is partial and source-biased.",
                coverage_geography="Global / EU-heavy depending on board",
                docs_url=getattr(collector, "base_url", None),
                terms_url=None,
            )
        )

    for item in UNSUPPORTED_SOURCES:
        existing = db.scalar(select(Source).where(Source.name == item["name"]))
        if existing:
            continue
        db.add(
            Source(
                name=item["name"],
                source_type="external",
                base_url=None,
                connector_type=item["source_key"],
                enabled=item["connector_status"] == "manual_import",
                connector_status=item["connector_status"],
                configuration={},
                coverage_notes=item["coverage_notes"],
            )
        )

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

    if not db.scalar(select(SearchQuery).limit(1)):
        defaults = [
            ("Senior Java Contractor", "Senior Java Contractor"),
            ("Java Spring Boot B2B", "Java Spring Boot B2B"),
            ("Cloud Architect Freelance", "Cloud Architect Freelance"),
            ("Kubernetes Consultant", "Kubernetes Consultant"),
            ("AI Engineer B2B", "AI Engineer B2B"),
            ("LLM Engineer Freelance", "LLM Engineer Freelance"),
            ("RAG Engineer", "RAG Engineer"),
            ("MLOps Engineer", "MLOps Engineer"),
        ]
        for name, text in defaults:
            db.add(
                SearchQuery(
                    name=name,
                    query_text=text,
                    countries=["IT", "CH", "DE", "AT", "FR", "NL", "BE", "LU", "IE", "ES", "GB", "US"],
                    role_families=[],
                    contract_types=["freelance", "b2b", "contractor"],
                    enabled=True,
                )
            )

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
