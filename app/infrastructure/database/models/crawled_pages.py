from enum import Enum
import uuid
from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Index,
    Integer,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.infrastructure.database.base import Base
from typing import Optional


class CrawlProviderEnum(str, Enum):
    SCRAPERAPI = "scraperapi"
    PLAYWRIGHT = "playwright"
    AXIOS = "axios"
    ZENROWS = "zenrows"
    FIRECRAWL = "firecrawl"
    MANUAL = "manual"


# =========================================================
# CRAWLED PAGES
# =========================================================


class CrawledPage(Base):
    __tablename__ = "crawled_pages"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    canonical_url_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("canonical_urls.id", ondelete="CASCADE"),
        nullable=False,
    )
    crawl_provider: Mapped[Optional[CrawlProviderEnum]] = mapped_column(
        SqlEnum(
            CrawlProviderEnum,
            name="crawl_provider",
            values_callable=lambda obj: [e.value for e in obj],
        )
    )
    raw_html: Mapped[Optional[str]] = mapped_column(Text)
    extracted_text: Mapped[Optional[str]] = mapped_column(Text)
    page_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSONB)
    content_hash: Mapped[Optional[str]] = mapped_column(Text)
    response_status_code: Mapped[Optional[int]] = mapped_column(Integer)
    crawl_duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    crawler_version: Mapped[Optional[str]] = mapped_column(Text)
    crawled_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    canonical_url = relationship(
        "CanonicalUrl",
        back_populates="crawled_pages",
    )
    __table_args__ = (
        Index("idx_crawled_pages_url", "canonical_url_id"),
        Index("idx_crawled_pages_provider", "crawl_provider"),
        Index("idx_crawled_pages_crawled_at", "crawled_at"),
    )