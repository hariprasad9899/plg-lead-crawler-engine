from datetime import datetime
import uuid

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database.base import Base


class JobConfigModel(Base):
    __tablename__ = "job_configs"

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

    name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    current_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        # job_configs <-> job_config_versions form a FK cycle. use_alter
        # emits this FK as a separate ALTER TABLE after both tables exist so
        # migrations / create_all can resolve table ordering.
        ForeignKey(
            "job_config_versions.id",
            use_alter=True,
            name="fk_job_configs_current_version",
        ),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )

    versions = relationship(
        "JobConfigVersionModel",
        back_populates="job_config",
        cascade="all, delete-orphan",
        order_by="JobConfigVersionModel.version_number",
        foreign_keys="JobConfigVersionModel.job_config_id",
    )

    current_version = relationship(
        "JobConfigVersionModel",
        foreign_keys=[current_version_id],
        post_update=True,
    )

    __table_args__ = (
        Index("idx_job_configs_tenant", "tenant_id"),
        Index("idx_job_configs_created_by", "created_by"),
    )
