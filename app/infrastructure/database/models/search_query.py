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
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database.base import Base


class QueryStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SearchQuery(Base):
    __tablename__ = "search_queries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuidv7()"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    job_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_runs.id", ondelete="CASCADE"),
        nullable=False,
    )

    query: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=50,
    )

    strategy: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
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

    llm_provider: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    llm_model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    job_run = relationship(
        "JobRun",
        back_populates="search_queries",
    )

    discovered_urls = relationship(
        "DiscoveredUrl",
        back_populates="search_query",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index(
            "idx_search_queries_tenant",
            "tenant_id",
        ),
        Index(
            "idx_search_queries_job_run",
            "job_run_id",
        ),
        Index(
            "idx_search_queries_tenant_status",
            "tenant_id",
            "status",
        ),
    )