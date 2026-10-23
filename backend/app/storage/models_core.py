from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.storage.db import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    base_url: Mapped[Optional[str]] = mapped_column(String(512))
    connector_type: Mapped[str] = mapped_column(String(64), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    connector_status: Mapped[str] = mapped_column(String(64), default="unsupported")
    verification_status: Mapped[str] = mapped_column(String(64), default="DISCOVERED")
    catalog_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(8))
    access_mode: Mapped[Optional[str]] = mapped_column(String(64))
    configuration: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    terms_url: Mapped[Optional[str]] = mapped_column(String(512))
    coverage_notes: Mapped[Optional[str]] = mapped_column(Text)
    coverage_geography: Mapped[Optional[str]] = mapped_column(Text)
    last_success_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_error_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[Optional[str]] = mapped_column(Text)
    last_validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    docs_url: Mapped[Optional[str]] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    jobs: Mapped[list[Job]] = relationship(back_populates="source")
    collection_runs: Mapped[list[CollectionRun]] = relationship(back_populates="source")
    verifications: Mapped[list[SourceVerification]] = relationship(back_populates="source")


class SourceVerification(Base):
    __tablename__ = "source_verifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sources.id"))
    catalog_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    http_status: Mapped[Optional[int]] = mapped_column(Integer)
    evidence: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    source: Mapped[Optional[Source]] = relationship(back_populates="verifications")


class SourceCredential(Base):
    """Fernet-encrypted secret bundle per credentialed connector_key (not Source FK)."""

    __tablename__ = "source_credentials"

    connector_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    ciphertext: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    updated_by: Mapped[Optional[str]] = mapped_column(String(128))


class SearchQuery(Base):
    __tablename__ = "search_queries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    countries: Mapped[list[str]] = mapped_column(JSON, default=list)
    role_families: Mapped[list[str]] = mapped_column(JSON, default=list)
    contract_types: Mapped[list[str]] = mapped_column(JSON, default=list)
    filters_extra: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    kind: Mapped[str] = mapped_column(String(32), default="focus", nullable=False)  # discovery | focus
    origin: Mapped[str] = mapped_column(String(32), default="user", nullable=False)
    schedule_hint: Mapped[str] = mapped_column(String(32), default="daily", nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class JobIntentMatch(Base):
    """Normative provenance: job matched to a research intent (discovery or focus)."""

    __tablename__ = "job_intent_matches"
    __table_args__ = (
        UniqueConstraint("job_id", "query_id", name="uq_job_intent_match"),
        Index("ix_job_intent_matches_query_id", "query_id"),
        Index("ix_job_intent_matches_job_id", "job_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    query_id: Mapped[int] = mapped_column(ForeignKey("search_queries.id", ondelete="CASCADE"), nullable=False)
    first_matched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_matched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CollectionRun(Base):
    __tablename__ = "collection_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    query_id: Mapped[Optional[int]] = mapped_column(ForeignKey("search_queries.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), default="pending")
    pages_scanned: Mapped[int] = mapped_column(Integer, default=0)
    records_received: Mapped[int] = mapped_column(Integer, default=0)
    records_inserted: Mapped[int] = mapped_column(Integer, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, default=0)
    duplicates_detected: Mapped[int] = mapped_column(Integer, default=0)
    errors_count: Mapped[int] = mapped_column(Integer, default=0)
    error_summary: Mapped[Optional[str]] = mapped_column(Text)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float)
    summary: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    source: Mapped[Source] = relationship(back_populates="collection_runs")


class CrawlerTick(Base):
    """UTC-day idempotency record for budgeted daily crawlers."""

    __tablename__ = "crawler_ticks"

    day: Mapped[date] = mapped_column(Date, primary_key=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    summary: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("source_id", "source_job_id", name="uq_jobs_source_native"),
        Index("ix_jobs_country_contract", "country_code", "contract_type"),
        Index("ix_jobs_published_at", "published_at"),
        Index("ix_jobs_canonical_url", "canonical_url"),
        Index("ix_jobs_description_hash", "description_hash"),
        # One canonical row per URL (app dedup + race safety). Non-canonical
        # duplicates may still share the URL if duplicate_of_job_id is used later.
        Index(
            "uq_jobs_canonical_url_when_canonical",
            "canonical_url",
            unique=True,
            postgresql_where=text("is_canonical IS TRUE"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    query_id: Mapped[Optional[int]] = mapped_column(ForeignKey("search_queries.id"))
    source_job_id: Mapped[str] = mapped_column(String(255), nullable=False)
    canonical_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    title_original: Mapped[str] = mapped_column(Text, nullable=False)
    title_normalized: Mapped[Optional[str]] = mapped_column(Text)
    company_original: Mapped[Optional[str]] = mapped_column(Text)
    company_normalized: Mapped[Optional[str]] = mapped_column(Text)
    description_original: Mapped[Optional[str]] = mapped_column(Text)
    description_hash: Mapped[Optional[str]] = mapped_column(String(64))
    location_original: Mapped[Optional[str]] = mapped_column(Text)
    country_code: Mapped[str] = mapped_column(String(8), default="unknown")
    region: Mapped[Optional[str]] = mapped_column(String(128))
    city: Mapped[Optional[str]] = mapped_column(String(128))
    remote_type: Mapped[str] = mapped_column(String(32), default="unknown")
    employment_type: Mapped[Optional[str]] = mapped_column(String(64))
    contract_type: Mapped[str] = mapped_column(String(32), default="unknown")
    contract_type_confidence: Mapped[Optional[float]] = mapped_column(Float)
    contract_evidence_kind: Mapped[str] = mapped_column(String(32), default="inferred")
    b2b_eligible: Mapped[Optional[bool]] = mapped_column(Boolean)
    b2b_evidence: Mapped[Optional[str]] = mapped_column(Text)
    residence_restriction: Mapped[str] = mapped_column(String(64), default="unclear")
    work_authorization_requirement: Mapped[Optional[str]] = mapped_column(Text)
    language_requirements: Mapped[list[str]] = mapped_column(JSON, default=list)
    seniority: Mapped[Optional[str]] = mapped_column(String(64))
    years_experience_min: Mapped[Optional[int]] = mapped_column(Integer)
    years_experience_max: Mapped[Optional[int]] = mapped_column(Integer)
    sector: Mapped[Optional[str]] = mapped_column(String(128))
    role_family: Mapped[Optional[str]] = mapped_column(String(128))
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), default="active_unverified")
    source_status: Mapped[Optional[str]] = mapped_column(String(64))
    collection_method: Mapped[str] = mapped_column(String(64), default="api")
    evidence_tier: Mapped[str] = mapped_column(String(16), default="standard")
    source_snapshot_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    classification_version: Mapped[Optional[str]] = mapped_column(String(32))
    duplicate_of_job_id: Mapped[Optional[int]] = mapped_column(ForeignKey("jobs.id"))
    is_canonical: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    source: Mapped[Source] = relationship(back_populates="jobs")
    skills: Mapped[list[JobSkill]] = relationship(back_populates="job", cascade="all, delete-orphan")
    rates: Mapped[list[JobRate]] = relationship(back_populates="job", cascade="all, delete-orphan")


# Forward refs for typing
from app.storage.models_skills import JobRate, JobSkill  # noqa: E402
