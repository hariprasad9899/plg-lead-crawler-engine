from datetime import datetime
from enum import Enum
import uuid

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Index,
    Integer,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class RunStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobRun(Base):
    __tablename__ = "job_runs"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuidv7()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    intent_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intent_jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    job_config_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_config_versions.id"),
        nullable=False,
    )
    status: Mapped[RunStatusEnum] = mapped_column(
        SqlEnum(
            RunStatusEnum,
            name="run_status",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=RunStatusEnum.PENDING,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    seed_urls_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    discovered_urls_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    processed_urls_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    qualified_leads_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    intent_job = relationship(
        "IntentJob",
        back_populates="job_runs",
    )
    job_config_version = relationship(
        "JobConfigVersionModel",
        back_populates="job_runs",
    )
    search_queries = relationship(
        "SearchQuery",
        back_populates="job_run",
        cascade="all, delete-orphan",
    )
    crawled_leads = relationship(
        "CrawledLead",
        back_populates="job_run",
        cascade="all, delete-orphan",
    )
    __table_args__ = (
        Index("idx_job_runs_tenant", "tenant_id"),
        Index("idx_job_runs_job", "intent_job_id"),
        Index("idx_job_runs_config", "job_config_version_id"),
        Index("idx_job_runs_tenant_status", "tenant_id", "status"),
    )