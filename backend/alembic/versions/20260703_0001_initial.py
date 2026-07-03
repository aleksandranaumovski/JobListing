"""initial job schema

Revision ID: 20260703_0001
Revises:
Create Date: 2026-07-03
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260703_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("base_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_sources_name", "sources", ["name"])

    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("source_key", sa.String(length=700), nullable=False),
        sa.Column("source_job_id", sa.String(length=200), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("company", sa.String(length=300), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("location", sa.String(length=250), nullable=True),
        sa.Column("category", sa.String(length=120), nullable=True),
        sa.Column("employment_type", sa.String(length=120), nullable=True),
        sa.Column("url", sa.String(length=1000), nullable=True),
        sa.Column("posted_at", sa.Date(), nullable=True),
        sa.Column("active_until", sa.Date(), nullable=True),
        sa.Column("salary", sa.String(length=250), nullable=True),
        sa.Column("is_new", sa.Boolean(), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("source_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("scraped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_id", "source_key", name="uq_jobs_source_key"),
    )
    for name, column in [
        ("ix_jobs_source_id", "source_id"),
        ("ix_jobs_source_job_id", "source_job_id"),
        ("ix_jobs_title", "title"),
        ("ix_jobs_city", "city"),
        ("ix_jobs_company", "company"),
        ("ix_jobs_category", "category"),
        ("ix_jobs_employment_type", "employment_type"),
        ("ix_jobs_posted_at", "posted_at"),
    ]:
        op.create_index(name, "jobs", [column])
    op.create_index("ix_jobs_source_id_created_at", "jobs", ["source_id", "created_at"])
    op.execute(
        """
        CREATE INDEX ix_jobs_search_vector ON jobs USING gin (
            to_tsvector('simple', coalesce(title,'') || ' ' || coalesce(company,'') || ' ' || coalesce(city,'') || ' ' || coalesce(raw_text,''))
        )
        """
    )


def downgrade() -> None:
    op.drop_table("jobs")
    op.drop_table("sources")
