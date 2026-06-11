from datetime import datetime
import uuid

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.lead import (
    LeadSourceEnum,
    LeadTypeEnum,
)


class CrawledLead(Base):
    """A per-run **observation** of a lead — an immutable snapshot of exactly
    what one ``job_run`` extracted from one crawled page.

    Observations are append-only history. They roll up into a single master
    ``Lead`` (via ``lead_id``) that holds the merged, current view. Keeping
    the raw snapshot here means a later/better merge rule can always be
    re-applied from the original data, and you can see how a company's data
    changed run-over-run.
    """

    __tablename__ = "crawled_leads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuidv7()"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    # The master lead this observation rolls up into (deduped by fingerprint).
    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ---- Provenance: which run / page / url produced this snapshot ----
    job_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    canonical_url_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("canonical_urls.id", ondelete="CASCADE"),
        nullable=False,
    )
    crawled_page_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crawled_pages.id", ondelete="SET NULL"),
        nullable=True,
    )

    lead_type: Mapped[LeadTypeEnum] = mapped_column(
        SqlEnum(
            LeadTypeEnum,
            name="lead_type",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=LeadTypeEnum.COMPANY,
    )
    source: Mapped[LeadSourceEnum] = mapped_column(
        SqlEnum(
            LeadSourceEnum,
            name="lead_source",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=LeadSourceEnum.CRAWL,
    )

    # ---- Lean typed snapshot (what THIS run saw) for run-over-run queries ----
    company_name: Mapped[str | None] = mapped_column(Text)
    company_domain: Mapped[str | None] = mapped_column(Text)
    industry: Mapped[str | None] = mapped_column(Text)
    employee_count: Mapped[int | None] = mapped_column(Integer)

    # Extraction confidence (0.0 - 1.0) for this run's extraction.
    confidence_score: Mapped[float | None] = mapped_column(Float)
    extraction_method: Mapped[str | None] = mapped_column(Text)

    # Full raw extraction payload from this run (audit / reprocessing).
    raw_extraction: Mapped[dict | None] = mapped_column(JSONB)
    # Signals observed in this specific run.
    signals: Mapped[dict | None] = mapped_column(JSONB)

    # Immutable: an observation is never updated, only appended.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # ---- Relationships ----
    lead = relationship("Lead", back_populates="observations")
    job_run = relationship("JobRun", back_populates="crawled_leads")
    canonical_url = relationship("CanonicalUrl")
    crawled_page = relationship("CrawledPage")

    __table_args__ = (
        # One observation per (run, canonical url) — re-extracting the same
        # page within a run upserts, not duplicates.
        UniqueConstraint(
            "job_run_id",
            "canonical_url_id",
            name="uq_crawled_leads_run_canonical",
        ),
        Index("idx_crawled_leads_tenant", "tenant_id"),
        Index("idx_crawled_leads_lead", "lead_id"),
        Index("idx_crawled_leads_job_run", "job_run_id"),
        Index("idx_crawled_leads_canonical", "canonical_url_id"),
    )
