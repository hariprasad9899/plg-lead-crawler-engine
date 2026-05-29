from enum import Enum
import uuid
from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.infrastructure.database.base import Base


class JobStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


# =========================================================
# INTENT JOBS
# =========================================================


class IntentJob(Base):
    __tablename__ = "intent_jobs"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    request_name: Mapped[str] = mapped_column(Text, nullable=False)
    original_query: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[JobStatusEnum] = mapped_column(
        SqlEnum(
            JobStatusEnum,
            name="job_status",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=JobStatusEnum.PENDING,
    )
    product_name: Mapped[str | None] = mapped_column(Text)
    product_description: Mapped[str | None] = mapped_column(Text)
    target_industries: Mapped[dict | None] = mapped_column(JSONB)
    target_countries: Mapped[dict | None] = mapped_column(JSONB)
    target_regions: Mapped[dict | None] = mapped_column(JSONB)
    min_company_size: Mapped[int | None] = mapped_column(Integer)
    max_company_size: Mapped[int | None] = mapped_column(Integer)
    target_personas: Mapped[dict | None] = mapped_column(JSONB)
    target_technologies: Mapped[dict | None] = mapped_column(JSONB)
    excluded_technologies: Mapped[dict | None] = mapped_column(JSONB)
    excluded_domains: Mapped[dict | None] = mapped_column(JSONB)
    buying_signals: Mapped[dict | None] = mapped_column(JSONB)
    negative_signals: Mapped[dict | None] = mapped_column(JSONB)
    signal_priority_weights: Mapped[dict | None] = mapped_column(JSONB)
    schedule_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="cron"
    )
    schedule_expression: Mapped[str] = mapped_column(
        Text, nullable=False, default="0 */6 * * *"
    )
    lead_score_threshold: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=70,
    )
    max_urls_per_run: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=50,
    )
    total_seed_urls: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    total_discovered_urls: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    total_processed_urls: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    total_qualified_leads: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    last_run_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    next_run_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
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
    generated_intents = relationship(
        "GeneratedIntent",
        back_populates="intent_job",
        cascade="all, delete-orphan",
    )
    __table_args__ = (
        Index("idx_intent_jobs_status", "status"),
        Index("idx_intent_jobs_next_run", "next_run_at"),
        Index("idx_intent_jobs_tenant", "tenant_id"),
        Index("idx_intent_jobs_created_by", "created_by"),
    )
