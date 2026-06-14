from datetime import datetime
from enum import Enum
import uuid
from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Index,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.infrastructure.database.base import Base


class JobStatusEnum(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class IntentJob(Base):
    __tablename__ = "intent_jobs"
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
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    request_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    original_query: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    status: Mapped[JobStatusEnum] = mapped_column(
        SqlEnum(
            JobStatusEnum,
            name="job_status",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=JobStatusEnum.ACTIVE,
    )

    # Set later, once intent generation has produced a config version to run.
    # Null at job-creation time, so this FK must be nullable.
    current_config_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_config_versions.id"),
        nullable=True,
    )
    schedule_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="cron",
    )
    schedule_expression: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="0 */6 * * *",
    )
    next_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    job_runs = relationship(
        "JobRun",
        back_populates="intent_job",
        cascade="all, delete-orphan",
    )
    current_config_version = relationship(
        "JobConfigVersionModel",
        foreign_keys=[current_config_version_id],
    )
    __table_args__ = (
        Index("idx_intent_jobs_status", "status"),
        # Scheduler dequeue: WHERE status = 'active' AND next_run_at <= now().
        # Partial composite index keeps only due/active jobs.
        Index(
            "idx_intent_jobs_due",
            "next_run_at",
            postgresql_where=text("status = 'active'"),
        ),
        Index("idx_intent_jobs_tenant", "tenant_id"),
        Index("idx_intent_jobs_created_by", "created_by"),
        # Supports "which jobs use config version X" lookups.
        Index("idx_intent_jobs_config_version", "current_config_version_id"),
    )
