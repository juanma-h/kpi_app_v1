"""add allowlist domains

Revision ID: 4b7c7d1c2a31
Revises: 135fd78cc608
Create Date: 2026-03-30 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4b7c7d1c2a31"
down_revision: Union[str, Sequence[str], None] = "135fd78cc608"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "allowlist_domains",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_allowlist_domains_domain"),
        "allowlist_domains",
        ["domain"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_allowlist_domains_domain"), table_name="allowlist_domains")
    op.drop_table("allowlist_domains")
