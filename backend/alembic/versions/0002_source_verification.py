"""source verification fields and table

Revision ID: 0002_source_verification
Revises: 0001_initial_schema
Create Date: 2026-10-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_source_verification"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("sources", "name", type_=sa.String(length=256), existing_type=sa.String(length=128))
    op.add_column("sources", sa.Column("verification_status", sa.String(length=64), server_default="DISCOVERED"))
    op.add_column("sources", sa.Column("catalog_id", sa.Integer(), nullable=True))
    op.add_column("sources", sa.Column("category", sa.String(length=8), nullable=True))
    op.add_column("sources", sa.Column("access_mode", sa.String(length=64), nullable=True))
    op.add_column("sources", sa.Column("last_validated_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_sources_catalog_id", "sources", ["catalog_id"])

    op.create_table(
        "source_verifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id"), nullable=True),
        sa.Column("catalog_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("http_status", sa.Integer(), nullable=True),
        sa.Column("evidence", sa.JSON(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("checked_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_source_verifications_catalog_id", "source_verifications", ["catalog_id"])


def downgrade() -> None:
    op.drop_index("ix_source_verifications_catalog_id", table_name="source_verifications")
    op.drop_table("source_verifications")
    op.drop_index("ix_sources_catalog_id", table_name="sources")
    op.drop_column("sources", "last_validated_at")
    op.drop_column("sources", "access_mode")
    op.drop_column("sources", "category")
    op.drop_column("sources", "catalog_id")
    op.drop_column("sources", "verification_status")
    op.alter_column("sources", "name", type_=sa.String(length=128), existing_type=sa.String(length=256))
