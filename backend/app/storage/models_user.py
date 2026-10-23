from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.storage.db import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    display_name: Mapped[str] = mapped_column(String(128), default="Default Freelance Profile")
    years_experience: Mapped[Optional[int]] = mapped_column(Integer)
    residence_country: Mapped[str] = mapped_column(String(8), default="IT")
    languages: Mapped[list[str]] = mapped_column(JSON, default=list)
    remote_preference: Mapped[str] = mapped_column(String(32), default="remote")
    contract_preference: Mapped[list[str]] = mapped_column(JSON, default=lambda: ["b2b", "freelance"])
    travel_willingness: Mapped[bool] = mapped_column(Boolean, default=False)
    min_rate_amount: Mapped[Optional[float]] = mapped_column(Float)
    target_rate_amount: Mapped[Optional[float]] = mapped_column(Float)
    rate_unit: Mapped[str] = mapped_column(String(16), default="day")
    rate_currency: Mapped[str] = mapped_column(String(8), default="EUR")
    monthly_availability_days: Mapped[Optional[int]] = mapped_column(Integer)
    goals_3m: Mapped[Optional[str]] = mapped_column(Text)
    goals_6m: Mapped[Optional[str]] = mapped_column(Text)
    goals_12m: Mapped[Optional[str]] = mapped_column(Text)
    sectors: Mapped[list[str]] = mapped_column(JSON, default=list)
    skill_priority_weights: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=lambda: {
            "demand": 0.25,
            "growth": 0.2,
            "rates": 0.15,
            "compatibility": 0.2,
            "accessibility": 0.1,
            "rarity": 0.05,
            "learning_cost": 0.05,
        },
    )
    dashboard_prefs: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class UserSkill(Base):
    __tablename__ = "user_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("user_profiles.id"), nullable=False)
    technology_id: Mapped[int] = mapped_column(ForeignKey("technologies.id"), nullable=False)
    level: Mapped[str] = mapped_column(String(32), default="intermediate")
    years: Mapped[Optional[float]] = mapped_column(Float)
    verifiable: Mapped[bool] = mapped_column(Boolean, default=False)
    learning_cost_days: Mapped[Optional[int]] = mapped_column(Integer)


class ApplicationOutcome(Base):
    __tablename__ = "application_outcomes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("user_profiles.id"), nullable=False)
    job_id: Mapped[Optional[int]] = mapped_column(ForeignKey("jobs.id"))
    applied_at: Mapped[date] = mapped_column(Date, nullable=False)
    channel: Mapped[Optional[str]] = mapped_column(String(64))
    intermediary: Mapped[Optional[str]] = mapped_column(String(128))
    requested_rate: Mapped[Optional[float]] = mapped_column(Float)
    offered_rate: Mapped[Optional[float]] = mapped_column(Float)
    rate_unit: Mapped[Optional[str]] = mapped_column(String(16))
    currency: Mapped[Optional[str]] = mapped_column(String(8))
    response: Mapped[Optional[str]] = mapped_column(String(64))
    interview: Mapped[Optional[bool]] = mapped_column(Boolean)
    outcome: Mapped[Optional[str]] = mapped_column(String(64))
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    billed_days: Mapped[Optional[float]] = mapped_column(Float)
    renewed: Mapped[Optional[bool]] = mapped_column(Boolean)
    revenue_amount: Mapped[Optional[float]] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SavedFilter(Base):
    __tablename__ = "saved_filters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AlertRule(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(64), nullable=False)
    configuration: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_evidence: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LlmModel(Base):
    __tablename__ = "llm_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    capabilities: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    healthy: Mapped[bool] = mapped_column(Boolean, default=False)
    last_health_check: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(String(64))
    entity_id: Mapped[Optional[str]] = mapped_column(String(64))
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
