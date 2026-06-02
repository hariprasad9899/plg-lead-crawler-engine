from datetime import datetime
from enum import Enum
import uuid

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class CrawlStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DiscoveredUrl(Base):
    __tablename__ = "discovered_urls"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuidv7()"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    canonical_url_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("canonical_urls.id", ondelete="CASCADE"),
        nullable=False,
    )

    search_query_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("search_queries.id", ondelete="CASCADE"),
        nullable=False,
    )

    source_engine: Mapped[str | None] = mapped_column(
        String(50),
    )

    priority_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=50,
    )

    discovery_depth: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    crawl_status: Mapped[CrawlStatusEnum] = mapped_column(
        SqlEnum(
            CrawlStatusEnum,
            name="crawl_status",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=CrawlStatusEnum.PENDING,
    )

    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    search_query = relationship(
        "SearchQuery",
        back_populates="discovered_urls",
    )

    canonical_url = relationship(
        "CanonicalUrl",
        back_populates="discovered_urls",
    )

    __table_args__ = (
        Index(
            "idx_discovered_tenant",
            "tenant_id",
        ),
        Index(
            "idx_discovered_canonical",
            "canonical_url_id",
        ),
        Index(
            "idx_discovered_crawl_status",
            "crawl_status",
        ),
    )