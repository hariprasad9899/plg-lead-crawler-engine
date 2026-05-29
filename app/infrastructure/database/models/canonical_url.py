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
# CANONICAL URLS
# =========================================================


class CanonicalUrl(Base):
    __tablename__ = "canonical_urls"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    normalized_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
    )
    url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    domain: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    title: Mapped[Optional[str]] = mapped_column(Text)
    content_hash: Mapped[Optional[str]] = mapped_column(Text)
    global_crawl_status: Mapped[CrawlStatusEnum] = mapped_column(
        SqlEnum(
            CrawlStatusEnum,
            name="crawl_status",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=CrawlStatusEnum.PENDING,
    )
    first_seen_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    last_crawled_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True))
    discovered_urls = relationship(
        "DiscoveredUrl",
        back_populates="canonical_url",
        cascade="all, delete-orphan",
    )
    crawled_pages = relationship(
        "CrawledPage",
        back_populates="canonical_url",
        cascade="all, delete-orphan",
    )
    __table_args__ = (
        Index("idx_canonical_domain", "domain"),
        Index("idx_canonical_crawl_status", "global_crawl_status"),
    )
