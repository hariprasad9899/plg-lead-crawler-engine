from datetime import datetime
import uuid

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.enums import (
    CrawlStatusEnum,
    crawl_status_type,
)


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
        crawl_status_type,
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
        # A tenant discovering the same canonical URL via the same query is a
        # duplicate, not new information. Enforce the dedup grain at the DB.
        UniqueConstraint(
            "tenant_id",
            "canonical_url_id",
            "search_query_id",
            name="uq_discovered_tenant_canonical_query",
        ),
        Index(
            "idx_discovered_tenant",
            "tenant_id",
        ),
        Index(
            "idx_discovered_canonical",
            "canonical_url_id",
        ),
        # Partial index for the per-tenant crawl worker dequeue:
        # WHERE crawl_status = 'pending', ordered by priority.
        Index(
            "idx_discovered_pending",
            "tenant_id",
            "priority_score",
            postgresql_where=text("crawl_status = 'pending'"),
        ),
    )