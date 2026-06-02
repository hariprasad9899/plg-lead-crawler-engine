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
    next_run_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    config_versions = relationship(
        "JobConfigVersion",
        back_populates="intent_job",
        cascade="all, delete-orphan",
        order_by="JobConfigVersion.version_number",
        foreign_keys="JobConfigVersion.intent_job_id",
    )
    job_runs = relationship(
        "JobRun",
        back_populates="intent_job",
        cascade="all, delete-orphan",
    )
    current_config = relationship(
        "JobConfigVersion",
        foreign_keys=[current_config_version_id],
    )
    __table_args__ = (
        Index("idx_intent_jobs_status", "status"),
        Index("idx_intent_jobs_next_run", "next_run_at"),
        Index("idx_intent_jobs_tenant", "tenant_id"),
        Index("idx_intent_jobs_created_by", "created_by"),
    )