"""LLM runtime config + prompt registry (ADR-010)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.storage.db import Base


class LlmRuntimeConfig(Base):
    """Singleton platform LLM settings (id=1)."""

    __tablename__ = "llm_runtime_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[str] = mapped_column(String(32), nullable=False, default="none")
    base_url: Mapped[Optional[str]] = mapped_column(String(512))
    model: Mapped[Optional[str]] = mapped_column(String(128))
    temperature: Mapped[float] = mapped_column(Float, default=0.1)
    timeout_s: Mapped[int] = mapped_column(Integer, default=120)
    max_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    api_key_ciphertext: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    enable_classify: Mapped[bool] = mapped_column(Boolean, default=True)
    enable_weekly_report: Mapped[bool] = mapped_column(Boolean, default=True)
    enable_study_advisor: Mapped[bool] = mapped_column(Boolean, default=True)
    enable_brief_narrative: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_by: Mapped[Optional[str]] = mapped_column(String(128))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class LlmPromptTemplate(Base):
    __tablename__ = "llm_prompt_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    purpose: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    active_version_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("llm_prompt_versions.id", use_alter=True, name="fk_prompt_active_ver")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    versions: Mapped[list[LlmPromptVersion]] = relationship(
        back_populates="template",
        foreign_keys="LlmPromptVersion.template_id",
        cascade="all, delete-orphan",
    )


class LlmPromptVersion(Base):
    __tablename__ = "llm_prompt_versions"
    __table_args__ = (UniqueConstraint("template_id", "version", name="uq_prompt_template_version"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("llm_prompt_templates.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    system_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    user_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="draft")
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[str]] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    meta: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    template: Mapped[LlmPromptTemplate] = relationship(
        back_populates="versions",
        foreign_keys=[template_id],
    )


class LlmAdminAudit(Base):
    __tablename__ = "llm_admin_audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    actor: Mapped[Optional[str]] = mapped_column(String(128))
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
