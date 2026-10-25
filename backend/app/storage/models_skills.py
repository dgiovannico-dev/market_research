from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.storage.db import Base


class Technology(Base):
    __tablename__ = "technologies"
    __table_args__ = (UniqueConstraint("canonical_name", name="uq_tech_canonical"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    canonical_name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    aliases: Mapped[list[str]] = mapped_column(JSON, default=list)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job_skills: Mapped[list[JobSkill]] = relationship(back_populates="technology")


class JobSkill(Base):
    __tablename__ = "job_skills"
    __table_args__ = (UniqueConstraint("job_id", "technology_id", "importance", name="uq_job_skill"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    technology_id: Mapped[int] = mapped_column(ForeignKey("technologies.id"), nullable=False)
    importance: Mapped[str] = mapped_column(String(32), default="mentioned")
    extraction_method: Mapped[str] = mapped_column(String(32), default="rules")
    evidence_kind: Mapped[str] = mapped_column(String(32), default="extracted")
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    evidence_span: Mapped[Optional[str]] = mapped_column(Text)
    model_version: Mapped[Optional[str]] = mapped_column(String(64))
    manually_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    job: Mapped["Job"] = relationship(back_populates="skills")
    technology: Mapped[Technology] = relationship(back_populates="job_skills")


class Certification(Base):
    __tablename__ = "certifications"
    __table_args__ = (UniqueConstraint("slug", name="uq_cert_slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    display_name: Mapped[str] = mapped_column(String(256), nullable=False)
    aliases: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job_links: Mapped[list["JobCertification"]] = relationship(back_populates="certification")


class JobCertification(Base):
    __tablename__ = "job_certifications"
    __table_args__ = (
        UniqueConstraint("job_id", "certification_id", "importance", name="uq_job_cert"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    certification_id: Mapped[int] = mapped_column(ForeignKey("certifications.id"), nullable=False)
    importance: Mapped[str] = mapped_column(String(32), default="mentioned")
    extraction_method: Mapped[str] = mapped_column(String(32), default="rules")
    evidence_span: Mapped[Optional[str]] = mapped_column(Text)

    certification: Mapped[Certification] = relationship(back_populates="job_links")



class JobRate(Base):
    __tablename__ = "job_rates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    amount_min: Mapped[Optional[float]] = mapped_column(Float)
    amount_max: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[Optional[str]] = mapped_column(String(8))
    unit: Mapped[str] = mapped_column(String(16), default="unknown")
    gross_or_net: Mapped[Optional[str]] = mapped_column(String(16))
    tax_included: Mapped[Optional[bool]] = mapped_column(Boolean)
    rate_type: Mapped[str] = mapped_column(String(32), default="advertised")
    evidence_text: Mapped[Optional[str]] = mapped_column(Text)
    extraction_method: Mapped[str] = mapped_column(String(32), default="rules")
    evidence_kind: Mapped[str] = mapped_column(String(32), default="extracted")
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    normalized_amount: Mapped[Optional[float]] = mapped_column(Float)
    normalization_currency: Mapped[Optional[str]] = mapped_column(String(8))
    fx_rate: Mapped[Optional[float]] = mapped_column(Float)
    fx_date: Mapped[Optional[date]] = mapped_column(Date)
    fx_source: Mapped[Optional[str]] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job: Mapped["Job"] = relationship(back_populates="rates")


class JobSnapshot(Base):
    __tablename__ = "job_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(String(32))
    title_hash: Mapped[Optional[str]] = mapped_column(String(64))
    description_hash: Mapped[Optional[str]] = mapped_column(String(64))
    rate_hash: Mapped[Optional[str]] = mapped_column(String(64))
    source_last_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class MarketMetricDaily(Base):
    __tablename__ = "market_metrics_daily"
    __table_args__ = (
        UniqueConstraint(
            "metric_date",
            "country_code",
            "role_family",
            "technology_id",
            "contract_type",
            "remote_type",
            "metric_name",
            name="uq_market_metric_daily",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    metric_date: Mapped[date] = mapped_column(Date, nullable=False)
    country_code: Mapped[str] = mapped_column(String(8), default="ALL")
    role_family: Mapped[str] = mapped_column(String(64), default="ALL")
    technology_id: Mapped[Optional[int]] = mapped_column(ForeignKey("technologies.id"))
    contract_type: Mapped[str] = mapped_column(String(32), default="ALL")
    remote_type: Mapped[str] = mapped_column(String(32), default="ALL")
    metric_name: Mapped[str] = mapped_column(String(128), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    numerator: Mapped[Optional[float]] = mapped_column(Float)
    denominator: Mapped[Optional[float]] = mapped_column(Float)
    sample_size: Mapped[int] = mapped_column(Integer, default=0)
    source_coverage: Mapped[Optional[str]] = mapped_column(Text)
    methodology_version: Mapped[str] = mapped_column(String(32), default="1.0.0")
    evidence_kind: Mapped[str] = mapped_column(String(32), default="derived")


class DuplicateGroup(Base):
    __tablename__ = "duplicate_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    canonical_job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    merge_reason: Mapped[str] = mapped_column(String(128), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    member_job_ids: Mapped[list[int]] = mapped_column(JSON, default=list)
    member_urls: Mapped[list[str]] = mapped_column(JSON, default=list)
    first_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    undone: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


from app.storage.models_core import Job  # noqa: E402
