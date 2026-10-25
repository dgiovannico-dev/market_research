"""llm_runtime_config + prompt registry

Revision ID: 0012_llm_runtime_prompts
Revises: 0011_certifications
Create Date: 2026-10-25
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "0012_llm_runtime_prompts"
down_revision: Union[str, None] = "0011_certifications"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(name: str) -> bool:
    bind = op.get_bind()
    return name in inspect(bind).get_table_names()


def upgrade() -> None:
    if not _has_table("llm_runtime_config"):
        op.create_table(
            "llm_runtime_config",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("provider", sa.String(length=32), nullable=False, server_default="none"),
            sa.Column("base_url", sa.String(length=512), nullable=True),
            sa.Column("model", sa.String(length=128), nullable=True),
            sa.Column("temperature", sa.Float(), nullable=False, server_default="0.1"),
            sa.Column("timeout_s", sa.Integer(), nullable=False, server_default="120"),
            sa.Column("max_tokens", sa.Integer(), nullable=True),
            sa.Column("api_key_ciphertext", sa.LargeBinary(), nullable=True),
            sa.Column(
                "enable_classify", sa.Boolean(), nullable=False, server_default=sa.text("true")
            ),
            sa.Column(
                "enable_weekly_report",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("true"),
            ),
            sa.Column(
                "enable_study_advisor",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("true"),
            ),
            sa.Column(
                "enable_brief_narrative",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
            sa.Column("updated_by", sa.String(length=128), nullable=True),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
        )
    if not _has_table("llm_prompt_templates"):
        op.create_table(
            "llm_prompt_templates",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("slug", sa.String(length=64), nullable=False),
            sa.Column("purpose", sa.String(length=64), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("active_version_id", sa.Integer(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.UniqueConstraint("slug", name="uq_llm_prompt_slug"),
        )
    if not _has_table("llm_prompt_versions"):
        op.create_table(
            "llm_prompt_versions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "template_id",
                sa.Integer(),
                sa.ForeignKey("llm_prompt_templates.id"),
                nullable=False,
            ),
            sa.Column("version", sa.Integer(), nullable=False),
            sa.Column("system_text", sa.Text(), nullable=False),
            sa.Column("user_text", sa.Text(), nullable=False),
            sa.Column("status", sa.String(length=16), nullable=False, server_default="draft"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_by", sa.String(length=128), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column("meta", sa.JSON(), nullable=True),
            sa.UniqueConstraint("template_id", "version", name="uq_prompt_template_version"),
        )
    # FK templates.active_version_id → versions (may already exist from create_all)
    bind = op.get_bind()
    fks = {fk["name"] for fk in inspect(bind).get_foreign_keys("llm_prompt_templates")}
    if "fk_prompt_active_ver" not in fks and _has_table("llm_prompt_versions"):
        op.create_foreign_key(
            "fk_prompt_active_ver",
            "llm_prompt_templates",
            "llm_prompt_versions",
            ["active_version_id"],
            ["id"],
        )
    if not _has_table("llm_admin_audits"):
        op.create_table(
            "llm_admin_audits",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("action", sa.String(length=64), nullable=False),
            sa.Column("actor", sa.String(length=128), nullable=True),
            sa.Column("details", sa.JSON(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
        )


def downgrade() -> None:
    if _has_table("llm_admin_audits"):
        op.drop_table("llm_admin_audits")
    bind = op.get_bind()
    if _has_table("llm_prompt_templates"):
        fks = {fk["name"] for fk in inspect(bind).get_foreign_keys("llm_prompt_templates")}
        if "fk_prompt_active_ver" in fks:
            op.drop_constraint("fk_prompt_active_ver", "llm_prompt_templates", type_="foreignkey")
    if _has_table("llm_prompt_versions"):
        op.drop_table("llm_prompt_versions")
    if _has_table("llm_prompt_templates"):
        op.drop_table("llm_prompt_templates")
    if _has_table("llm_runtime_config"):
        op.drop_table("llm_runtime_config")
