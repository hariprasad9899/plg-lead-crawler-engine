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
from typing import Optional


class CrawlStatusEnum(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    CRAWLING = "crawling"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"


# =========================================================
# DISCOVERED URLS
# =========================================================


class DiscoveredUrl(Base):
    __tablename__ = "discovered_urls"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
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
    source_engine: Mapped[Optional[str]] = mapped_column(String(50))
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
    discovered_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    canonical_url = relationship(
        "CanonicalUrl",
        back_populates="discovered_urls",
    )
    search_query = relationship(
        "SearchQuery",
        back_populates="discovered_urls",
    )
    __table_args__ = (
        Index("idx_discovered_tenant", "tenant_id"),
        Index("idx_discovered_canonical", "canonical_url_id"),
        Index("idx_discovered_crawl_status", "crawl_status"),
    )