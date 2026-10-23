"""Demand Compass: SearchQuery kind + job_intent_matches

Revision ID: 0004_research_intents
Revises: 0003_profile_dashboard_prefs
Create Date: 2026-10-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_research_intents"
down_revision: Union[str, None] = "0003_profile_dashboard_prefs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_names(table: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table not in inspector.get_table_names():
        return set()
    return {c["name"] for c in inspector.get_columns(table)}


def upgrade() -> None:
    cols = _column_names("search_queries")
    if "filters_extra" not in cols:
        op.add_column("search_queries", sa.Column("filters_extra", sa.JSON(), nullable=True))
    if "kind" not in cols:
        op.add_column(
            "search_queries",
            sa.Column("kind", sa.String(length=32), nullable=False, server_default="focus"),
        )
    if "origin" not in cols:
        op.add_column(
            "search_queries",
            sa.Column("origin", sa.String(length=32), nullable=False, server_default="user"),
        )
    if "schedule_hint" not in cols:
        op.add_column(
            "search_queries",
            sa.Column("schedule_hint", sa.String(length=32), nullable=False, server_default="daily"),
        )
    if "deleted_at" not in cols:
        op.add_column(
            "search_queries",
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        )

    # Existing rows were persona focus starters before Demand Compass.
    op.execute(
        sa.text(
            "UPDATE search_queries SET kind = 'focus', origin = 'seed_focus' "
            "WHERE origin = 'user' OR origin IS NULL OR origin = ''"
        )
    )

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "job_intent_matches" not in inspector.get_table_names():
        op.create_table(
            "job_intent_matches",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "job_id",
                sa.Integer(),
                sa.ForeignKey("jobs.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "query_id",
                sa.Integer(),
                sa.ForeignKey("search_queries.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("first_matched_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("last_matched_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.UniqueConstraint("job_id", "query_id", name="uq_job_intent_match"),
        )
        op.create_index("ix_job_intent_matches_query_id", "job_intent_matches", ["query_id"])
        op.create_index("ix_job_intent_matches_job_id", "job_intent_matches", ["job_id"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "job_intent_matches" in inspector.get_table_names():
        op.drop_index("ix_job_intent_matches_job_id", table_name="job_intent_matches")
        op.drop_index("ix_job_intent_matches_query_id", table_name="job_intent_matches")
        op.drop_table("job_intent_matches")
    cols = _column_names("search_queries")
    for name in ("deleted_at", "schedule_hint", "origin", "kind", "filters_extra"):
        if name in cols:
            op.drop_column("search_queries", name)
