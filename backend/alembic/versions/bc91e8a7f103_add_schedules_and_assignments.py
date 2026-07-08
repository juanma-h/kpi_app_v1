"""add schedules and assignments

Revision ID: bc91e8a7f103
Revises: 95f7d7d8b721
Create Date: 2026-03-31 00:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bc91e8a7f103"
down_revision: Union[str, Sequence[str], None] = "95f7d7d8b721"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "schedule_templates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("timezone_name", sa.String(length=64), nullable=False),
        sa.Column("grace_minutes", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_schedule_templates_name"), "schedule_templates", ["name"], unique=True)

    op.create_table(
        "schedule_template_slots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("schedule_template_id", sa.Integer(), nullable=False),
        sa.Column("weekday", sa.String(length=10), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.ForeignKeyConstraint(["schedule_template_id"], ["schedule_templates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("schedule_template_id", "weekday", name="uq_schedule_template_slots_weekday"),
    )
    op.create_index(
        op.f("ix_schedule_template_slots_schedule_template_id"),
        "schedule_template_slots",
        ["schedule_template_id"],
        unique=False,
    )

    op.create_table(
        "user_schedule_assignments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("schedule_template_id", sa.Integer(), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.String(length=255), nullable=True),
        sa.Column("assigned_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["assigned_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["schedule_template_id"], ["schedule_templates.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_schedule_assignments_schedule_template_id"), "user_schedule_assignments", ["schedule_template_id"], unique=False)
    op.create_index(op.f("ix_user_schedule_assignments_user_id"), "user_schedule_assignments", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_schedule_assignments_user_id"), table_name="user_schedule_assignments")
    op.drop_index(op.f("ix_user_schedule_assignments_schedule_template_id"), table_name="user_schedule_assignments")
    op.drop_table("user_schedule_assignments")
    op.drop_index(op.f("ix_schedule_template_slots_schedule_template_id"), table_name="schedule_template_slots")
    op.drop_table("schedule_template_slots")
    op.drop_index(op.f("ix_schedule_templates_name"), table_name="schedule_templates")
    op.drop_table("schedule_templates")
