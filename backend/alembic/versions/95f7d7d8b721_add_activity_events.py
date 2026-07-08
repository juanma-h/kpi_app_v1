"""add activity events

Revision ID: 95f7d7d8b721
Revises: 4b7c7d1c2a31
Create Date: 2026-03-31 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "95f7d7d8b721"
down_revision: Union[str, Sequence[str], None] = "4b7c7d1c2a31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "activity_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("shift_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("allowlist_domain_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=20), nullable=False),
        sa.Column("source_url", sa.String(length=2048), nullable=False),
        sa.Column("source_domain", sa.String(length=255), nullable=False),
        sa.Column("page_title", sa.String(length=255), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("event_data", sa.JSON(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["allowlist_domain_id"], ["allowlist_domains.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["shift_id"], ["shifts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_activity_events_allowlist_domain_id"), "activity_events", ["allowlist_domain_id"], unique=False)
    op.create_index(op.f("ix_activity_events_event_type"), "activity_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_activity_events_occurred_at"), "activity_events", ["occurred_at"], unique=False)
    op.create_index(op.f("ix_activity_events_session_id"), "activity_events", ["session_id"], unique=False)
    op.create_index(op.f("ix_activity_events_shift_id"), "activity_events", ["shift_id"], unique=False)
    op.create_index(op.f("ix_activity_events_source_domain"), "activity_events", ["source_domain"], unique=False)
    op.create_index(op.f("ix_activity_events_user_id"), "activity_events", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_activity_events_user_id"), table_name="activity_events")
    op.drop_index(op.f("ix_activity_events_source_domain"), table_name="activity_events")
    op.drop_index(op.f("ix_activity_events_shift_id"), table_name="activity_events")
    op.drop_index(op.f("ix_activity_events_session_id"), table_name="activity_events")
    op.drop_index(op.f("ix_activity_events_occurred_at"), table_name="activity_events")
    op.drop_index(op.f("ix_activity_events_event_type"), table_name="activity_events")
    op.drop_index(op.f("ix_activity_events_allowlist_domain_id"), table_name="activity_events")
    op.drop_table("activity_events")
