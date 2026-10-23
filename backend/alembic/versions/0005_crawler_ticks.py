"""Demand Compass: crawler_ticks UTC-day idempotency

Revision ID: 0005_crawler_ticks
Revises: 0004_research_intents
Create Date: 2026-10-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005_crawler_ticks"
down_revision: Union[str, None] = "0004_research_intents"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "crawler_ticks" not in inspector.get_table_names():
        op.create_table(
            "crawler_ticks",
            sa.Column("day", sa.Date(), primary_key=True),
            sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
            sa.Column("summary", sa.JSON(), nullable=True),
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "crawler_ticks" in inspector.get_table_names():
        op.drop_table("crawler_ticks")
