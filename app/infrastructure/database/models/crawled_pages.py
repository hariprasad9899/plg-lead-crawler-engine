from datetime import datetime
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

from app.infrastructure.database.base import Base


class CrawlProviderEnum(str, Enum):
    FIRECRAWL = "firecrawl"
    JINA = "jina"
    PLAYWRIGHT = "playwright"
    SCRAPINGBEE = "scrapingbee"
    CUSTOM = "custom"


class CrawledPage(Base):
    __tablename__ = "crawled_pages"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuidv7()"),
    )
    canonical_url_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("canonical_urls.id", ondelete="CASCADE"),
        nullable=False,
    )
    crawl_provider: Mapped[CrawlProviderEnum | None] = mapped_column(
        SqlEnum(
            CrawlProviderEnum,
            name="crawl_provider",
            values_callable=lambda obj: [e.value for e in obj],
        ),
    )
    raw_html: Mapped[str | None] = mapped_column(
        Text,
    )
    extracted_text: Mapped[str | None] = mapped_column(
        Text,
    )
    crawl_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
    )
    content_hash: Mapped[str | None] = mapped_column(
        Text,
    )
    response_status_code: Mapped[int | None] = mapped_column(
        Integer,
    )
    crawl_duration_ms: Mapped[int | None] = mapped_column(
        Integer,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
    )
    crawler_version: Mapped[str | None] = mapped_column(
        Text,
    )
    crawled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    canonical_url = relationship(
        "CanonicalUrl",
        back_populates="crawled_pages",
    )
    __table_args__ = (
        Index(
            "idx_crawled_pages_canonical",
            "canonical_url_id",
        ),
        Index(
            "idx_crawled_pages_crawled_at",
            "crawled_at",
        ),
        Index(
            "idx_crawled_pages_provider",
            "crawl_provider",
        ),
    )