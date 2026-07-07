"""users table and job moderation columns

Revision ID: 20260707_0002
Revises: 20260703_0001
Create Date: 2026-07-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260707_0002"
down_revision = "20260703_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("hashed_password", sa.String(length=200), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.add_column("jobs", sa.Column("status", sa.String(length=20), nullable=False, server_default="approved"))
    op.add_column("jobs", sa.Column("created_by_id", postgresql.UUID(as_uuid=False), nullable=True))
    op.create_foreign_key("fk_jobs_created_by_id_users", "jobs", "users", ["created_by_id"], ["id"], ondelete="SET NULL")
    op.create_index("ix_jobs_status", "jobs", ["status"])
    op.create_index("ix_jobs_created_by_id", "jobs", ["created_by_id"])


def downgrade() -> None:
    op.drop_index("ix_jobs_created_by_id", table_name="jobs")
    op.drop_index("ix_jobs_status", table_name="jobs")
    op.drop_constraint("fk_jobs_created_by_id_users", "jobs", type_="foreignkey")
    op.drop_column("jobs", "created_by_id")
    op.drop_column("jobs", "status")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
