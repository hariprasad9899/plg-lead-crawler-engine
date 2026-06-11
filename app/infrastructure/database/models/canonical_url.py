from datetime import datetime
import uuid

from sqlalchemy import (
    DateTime,
    Index,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.enums import (
    CrawlStatusEnum,
    crawl_status_type,
)


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
        crawl_status_type,
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
        # Partial index for the global crawl worker dequeue:
        # WHERE global_crawl_status = 'pending'. A plain index on a
        # low-cardinality status column is near-useless; the partial index
        # stays tiny and targets exactly the rows workers poll for.
        Index(
            "idx_canonical_pending",
            "first_seen_at",
            postgresql_where=text("global_crawl_status = 'pending'"),
        ),
    )