from datetime import datetime
import uuid

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class GeneratedIntent(Base):
    __tablename__ = "generated_intents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuidv7()"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    job_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_runs.id"),
        nullable=False,
    )

    intent_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    job_run = relationship(
        "JobRun",
        back_populates="generated_intents",
    )

    search_queries = relationship(
        "SearchQuery",
        back_populates="generated_intent",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index(
            "idx_generated_intents_tenant",
            "tenant_id",
        ),
        Index(
            "idx_generated_intents_run",
            "job_run_id",
        ),
    )