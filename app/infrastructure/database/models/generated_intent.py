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

# =========================================================
# GENERATED INTENTS
# =========================================================


class GeneratedIntent(Base):
    __tablename__ = "generated_intents"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    intent_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intent_jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    intent_text: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=50,
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    intent_job = relationship(
        "IntentJob",
        back_populates="generated_intents",
    )
    search_queries = relationship(
        "SearchQuery",
        back_populates="generated_intent",
        cascade="all, delete-orphan",
    )
    __table_args__ = (Index("idx_generated_intents_job", "intent_job_id"),)
