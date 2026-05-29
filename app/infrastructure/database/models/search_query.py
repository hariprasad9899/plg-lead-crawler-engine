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


class QueryStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# =========================================================
# SEARCH QUERIES
# =========================================================


class SearchQuery(Base):
    __tablename__ = "search_queries"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    generated_intent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("generated_intents.id", ondelete="CASCADE"),
        nullable=False,
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str | None] = mapped_column(String(50))
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=50,
    )
    status: Mapped[QueryStatusEnum] = mapped_column(
        SqlEnum(
            QueryStatusEnum,
            name="query_status",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=QueryStatusEnum.PENDING,
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    generated_intent = relationship(
        "GeneratedIntent",
        back_populates="search_queries",
    )
    discovered_urls = relationship(
        "DiscoveredUrl",
        back_populates="search_query",
        cascade="all, delete-orphan",
    )
    __table_args__ = (Index("idx_search_queries_status", "status"),)
