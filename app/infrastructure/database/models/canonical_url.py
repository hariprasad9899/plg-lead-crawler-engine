from datetime import datetime
from enum import Enum
import uuid

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    Index,
    Text,
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


class CanonicalUrl(Base):
    __tablename__ = "canonical_urls"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuidv7()"),
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

    title: Mapped[str | None] = mapped_column(
        Text,
    )

    content_hash: Mapped[str | None] = mapped_column(
        Text,
    )

    global_crawl_status: Mapped[CrawlStatusEnum] = mapped_column(
        SqlEnum(
            CrawlStatusEnum,
            name="crawl_status",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=CrawlStatusEnum.PENDING,
    )

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    last_crawled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    discovered_urls = relationship(
        "DiscoveredUrl",
        back_populates="canonical_url",
    )

    crawled_pages = relationship(
        "CrawledPage",
        back_populates="canonical_url",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index(
            "idx_canonical_domain",
            "domain",
        ),
        Index(
            "idx_canonical_crawl_status",
            "global_crawl_status",
        ),
    )