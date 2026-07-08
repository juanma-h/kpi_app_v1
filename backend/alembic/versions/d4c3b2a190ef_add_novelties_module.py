"""add novelties module

Revision ID: d4c3b2a190ef
Revises: bc91e8a7f103
Create Date: 2026-04-11 18:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d4c3b2a190ef"
down_revision: Union[str, Sequence[str], None] = "bc91e8a7f103"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "operational_areas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_operational_areas_code"), "operational_areas", ["code"], unique=True)
    op.create_index(op.f("ix_operational_areas_name"), "operational_areas", ["name"], unique=True)

    op.create_table(
        "source_systems",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("allowlist_domain_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["allowlist_domain_id"], ["allowlist_domains.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_source_systems_allowlist_domain_id"), "source_systems", ["allowlist_domain_id"], unique=False)
    op.create_index(op.f("ix_source_systems_code"), "source_systems", ["code"], unique=True)
    op.create_index(op.f("ix_source_systems_name"), "source_systems", ["name"], unique=True)

    op.create_table(
        "novelties",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("area_id", sa.Integer(), nullable=False),
        sa.Column("source_system_id", sa.Integer(), nullable=False),
        sa.Column("reported_by_user_id", sa.Integer(), nullable=False),
        sa.Column("assigned_user_id", sa.Integer(), nullable=True),
        sa.Column("reported_shift_id", sa.Integer(), nullable=True),
        sa.Column("reported_session_id", sa.Integer(), nullable=True),
        sa.Column("external_reference", sa.String(length=120), nullable=True),
        sa.Column("order_reference", sa.String(length=120), nullable=True),
        sa.Column("customer_reference", sa.String(length=120), nullable=True),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("novelty_type", sa.String(length=80), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("extra_data", sa.JSON(), nullable=True),
        sa.Column("reported_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("first_action_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["area_id"], ["operational_areas.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["assigned_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["reported_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reported_session_id"], ["sessions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["reported_shift_id"], ["shifts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_system_id"], ["source_systems.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_novelties_area_id"), "novelties", ["area_id"], unique=False)
    op.create_index(op.f("ix_novelties_assigned_user_id"), "novelties", ["assigned_user_id"], unique=False)
    op.create_index(op.f("ix_novelties_external_reference"), "novelties", ["external_reference"], unique=False)
    op.create_index(op.f("ix_novelties_novelty_type"), "novelties", ["novelty_type"], unique=False)
    op.create_index(op.f("ix_novelties_order_reference"), "novelties", ["order_reference"], unique=False)
    op.create_index(op.f("ix_novelties_priority"), "novelties", ["priority"], unique=False)
    op.create_index(op.f("ix_novelties_reported_at"), "novelties", ["reported_at"], unique=False)
    op.create_index(op.f("ix_novelties_reported_by_user_id"), "novelties", ["reported_by_user_id"], unique=False)
    op.create_index(op.f("ix_novelties_reported_session_id"), "novelties", ["reported_session_id"], unique=False)
    op.create_index(op.f("ix_novelties_reported_shift_id"), "novelties", ["reported_shift_id"], unique=False)
    op.create_index(op.f("ix_novelties_source_system_id"), "novelties", ["source_system_id"], unique=False)
    op.create_index(op.f("ix_novelties_status"), "novelties", ["status"], unique=False)

    op.create_table(
        "novelty_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("novelty_id", sa.Integer(), nullable=False),
        sa.Column("author_user_id", sa.Integer(), nullable=False),
        sa.Column("shift_id", sa.Integer(), nullable=True),
        sa.Column("session_id", sa.Integer(), nullable=True),
        sa.Column("work_date", sa.Date(), nullable=False),
        sa.Column("log_type", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("worked_minutes", sa.Integer(), nullable=True),
        sa.Column("status_after", sa.String(length=20), nullable=True),
        sa.Column("logged_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["author_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["novelty_id"], ["novelties.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["shift_id"], ["shifts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_novelty_logs_author_user_id"), "novelty_logs", ["author_user_id"], unique=False)
    op.create_index(op.f("ix_novelty_logs_log_type"), "novelty_logs", ["log_type"], unique=False)
    op.create_index(op.f("ix_novelty_logs_novelty_id"), "novelty_logs", ["novelty_id"], unique=False)
    op.create_index(op.f("ix_novelty_logs_session_id"), "novelty_logs", ["session_id"], unique=False)
    op.create_index(op.f("ix_novelty_logs_shift_id"), "novelty_logs", ["shift_id"], unique=False)
    op.create_index(op.f("ix_novelty_logs_status_after"), "novelty_logs", ["status_after"], unique=False)
    op.create_index(op.f("ix_novelty_logs_work_date"), "novelty_logs", ["work_date"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_novelty_logs_work_date"), table_name="novelty_logs")
    op.drop_index(op.f("ix_novelty_logs_status_after"), table_name="novelty_logs")
    op.drop_index(op.f("ix_novelty_logs_shift_id"), table_name="novelty_logs")
    op.drop_index(op.f("ix_novelty_logs_session_id"), table_name="novelty_logs")
    op.drop_index(op.f("ix_novelty_logs_novelty_id"), table_name="novelty_logs")
    op.drop_index(op.f("ix_novelty_logs_log_type"), table_name="novelty_logs")
    op.drop_index(op.f("ix_novelty_logs_author_user_id"), table_name="novelty_logs")
    op.drop_table("novelty_logs")

    op.drop_index(op.f("ix_novelties_status"), table_name="novelties")
    op.drop_index(op.f("ix_novelties_source_system_id"), table_name="novelties")
    op.drop_index(op.f("ix_novelties_reported_shift_id"), table_name="novelties")
    op.drop_index(op.f("ix_novelties_reported_session_id"), table_name="novelties")
    op.drop_index(op.f("ix_novelties_reported_by_user_id"), table_name="novelties")
    op.drop_index(op.f("ix_novelties_reported_at"), table_name="novelties")
    op.drop_index(op.f("ix_novelties_priority"), table_name="novelties")
    op.drop_index(op.f("ix_novelties_order_reference"), table_name="novelties")
    op.drop_index(op.f("ix_novelties_novelty_type"), table_name="novelties")
    op.drop_index(op.f("ix_novelties_external_reference"), table_name="novelties")
    op.drop_index(op.f("ix_novelties_assigned_user_id"), table_name="novelties")
    op.drop_index(op.f("ix_novelties_area_id"), table_name="novelties")
    op.drop_table("novelties")

    op.drop_index(op.f("ix_source_systems_name"), table_name="source_systems")
    op.drop_index(op.f("ix_source_systems_code"), table_name="source_systems")
    op.drop_index(op.f("ix_source_systems_allowlist_domain_id"), table_name="source_systems")
    op.drop_table("source_systems")

    op.drop_index(op.f("ix_operational_areas_name"), table_name="operational_areas")
    op.drop_index(op.f("ix_operational_areas_code"), table_name="operational_areas")
    op.drop_table("operational_areas")
