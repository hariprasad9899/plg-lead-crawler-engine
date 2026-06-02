from datetime import datetime
from typing import Any
import uuid

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class JobConfigVersion(Base):
    __tablename__ = "job_config_versions"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuidv7()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    intent_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intent_jobs.id"),
        nullable=False,
    )
    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    config: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    intent_job = relationship(
        "IntentJob",
        back_populates="config_versions",
        foreign_keys=[intent_job_id],
    )
    job_runs = relationship(
        "JobRun",
        back_populates="job_config_version",
    )
    __table_args__ = (
        UniqueConstraint(
            "intent_job_id",
            "version_number",
            name="uq_job_config_versions_job_version",
        ),
        Index(
            "idx_job_config_versions_tenant",
            "tenant_id",
        ),
    )