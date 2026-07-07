from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    base_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    jobs: Mapped[list["Job"]] = relationship(back_populates="source")


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("source_id", "source_key", name="uq_jobs_source_key"),
        Index("ix_jobs_source_id_created_at", "source_id", "created_at"),
        Index("ix_jobs_city", "city"),
        Index("ix_jobs_company", "company"),
        Index("ix_jobs_category", "category"),
        Index("ix_jobs_employment_type", "employment_type"),
        Index("ix_jobs_posted_at", "posted_at"),
        Index("ix_jobs_status", "status"),
    )

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"), index=True)
    source_key: Mapped[str] = mapped_column(String(700))
    source_job_id: Mapped[str | None] = mapped_column(String(200), index=True)

    title: Mapped[str] = mapped_column(String(500), index=True)
    company: Mapped[str | None] = mapped_column(String(300))
    city: Mapped[str | None] = mapped_column(String(120))
    location: Mapped[str | None] = mapped_column(String(250))
    category: Mapped[str | None] = mapped_column(String(120))
    employment_type: Mapped[str | None] = mapped_column(String(120))
    url: Mapped[str | None] = mapped_column(String(1000))
    posted_at: Mapped[datetime | None] = mapped_column(Date)
    active_until: Mapped[datetime | None] = mapped_column(Date)
    salary: Mapped[str | None] = mapped_column(String(250))
    is_new: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default=STATUS_APPROVED)
    created_by_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), index=True, default=None
    )
    raw_text: Mapped[str | None] = mapped_column(Text)
    source_payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    source: Mapped[Source] = relationship(back_populates="jobs")
