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

    job_config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "job_configs.id",
            ondelete="CASCADE",
        ),
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

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    job_config = relationship(
        "JobConfig",
        back_populates="versions",
        foreign_keys=[job_config_id],
    )

    intent_jobs = relationship(
        "IntentJob",
        back_populates="selected_config_version",
    )

    job_runs = relationship(
        "JobRun",
        back_populates="job_config_version",
    )

    __table_args__ = (
        UniqueConstraint(
            "job_config_id",
            "version_number",
            name="uq_job_config_versions_config_version",
        ),
        Index(
            "idx_job_config_versions_tenant",
            "tenant_id",
        ),
        Index(
            "idx_job_config_versions_job_config",
            "job_config_id",
        ),
    )
