from datetime import datetime
from enum import Enum
import uuid

from sqlalchemy import (
    Boolean,
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


# ---------------------------------------------------------------------------
# Shared lead enums (used by both the master ``leads`` table and the
# per-run ``crawled_leads`` observation table).
# ---------------------------------------------------------------------------
class LeadTypeEnum(str, Enum):
    """What kind of entity this lead represents."""

    COMPANY = "company"
    PERSON = "person"


class LeadStatusEnum(str, Enum):
    """Lead qualification / funnel lifecycle. Lives on the master record."""

    NEW = "new"
    ENRICHING = "enriching"
    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"
    NEEDS_REVIEW = "needs_review"
    EXPORTED = "exported"


class EnrichmentStatusEnum(str, Enum):
    """State of third-party enrichment for this lead."""

    NONE = "none"
    PENDING = "pending"
    ENRICHED = "enriched"
    PARTIAL = "partial"
    FAILED = "failed"


class LeadSourceEnum(str, Enum):
    """How a lead / observation was acquired."""

    CRAWL = "crawl"
    ENRICHMENT = "enrichment"
    MANUAL = "manual"
    IMPORT = "import"


class ContactEmailStatusEnum(str, Enum):
    UNVERIFIED = "unverified"
    VALID = "valid"
    INVALID = "invalid"
    CATCH_ALL = "catch_all"


class Lead(Base):
    """Master lead: the deduplicated, evolving "current best view" of one
    company (or person) for a tenant.

    There is **at most one Lead per (tenant, fingerprint)** — the unique
    constraint enforces it at the database level, so the same company found
    across many runs collapses to a single record. Each run still records
    what it saw in ``crawled_leads`` (the immutable observation/history); the
    Lead holds the merged result of those observations.

    Merge strategy is applied in application code at upsert time (last-write,
    fill-if-empty, source-priority, etc.) — see the lead ingestion service.
    """

    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuidv7()"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    # Stable dedup key (e.g. hash of normalized domain / primary email). The
    # same company across runs resolves to the same fingerprint -> same Lead.
    fingerprint: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # The company's primary URL. Kept nullable + SET NULL so pruning the
    # global URL table never destroys a tenant's lead.
    canonical_url_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("canonical_urls.id", ondelete="SET NULL"),
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

    # ---- Merged firmographic "best" values (UPDATED over time) ----
    company_name: Mapped[str | None] = mapped_column(Text)
    company_domain: Mapped[str | None] = mapped_column(Text)
    company_website: Mapped[str | None] = mapped_column(Text)
    industry: Mapped[str | None] = mapped_column(Text)
    employee_count: Mapped[int | None] = mapped_column(Integer)
    employee_range: Mapped[str | None] = mapped_column(Text)
    revenue_range: Mapped[str | None] = mapped_column(Text)
    country: Mapped[str | None] = mapped_column(Text)
    region: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str | None] = mapped_column(Text)
    linkedin_url: Mapped[str | None] = mapped_column(Text)

    # ---- Cached "primary contact" for single-row display/sort ----
    primary_contact_name: Mapped[str | None] = mapped_column(Text)
    primary_contact_title: Mapped[str | None] = mapped_column(Text)
    primary_contact_email: Mapped[str | None] = mapped_column(Text)
    primary_contact_phone: Mapped[str | None] = mapped_column(Text)

    # ---- Qualification lifecycle (lives on the master, not per run) ----
    status: Mapped[LeadStatusEnum] = mapped_column(
        SqlEnum(
            LeadStatusEnum,
            name="lead_status",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=LeadStatusEnum.NEW,
    )
    qualification_score: Mapped[int | None] = mapped_column(Integer)
    confidence_score: Mapped[float | None] = mapped_column(Float)
    disqualified_reason: Mapped[str | None] = mapped_column(Text)

    # ---- Expandable JSONB long tail (no migration to grow) ----
    firmographics: Mapped[dict | None] = mapped_column(JSONB)
    signals: Mapped[dict | None] = mapped_column(JSONB)
    enrichment: Mapped[dict | None] = mapped_column(JSONB)
    custom_fields: Mapped[dict | None] = mapped_column(JSONB)

    # ---- Enrichment lifecycle ----
    enrichment_status: Mapped[EnrichmentStatusEnum] = mapped_column(
        SqlEnum(
            EnrichmentStatusEnum,
            name="lead_enrichment_status",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=EnrichmentStatusEnum.NONE,
    )
    enriched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # ---- Downstream CRM sync ----
    external_id: Mapped[str | None] = mapped_column(Text)
    synced_to_crm: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    exported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # ---- Freshness / dedup bookkeeping ----
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    times_seen: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )

    # ---- Relationships ----
    canonical_url = relationship("CanonicalUrl")
    observations = relationship(
        "CrawledLead",
        back_populates="lead",
        cascade="all, delete-orphan",
    )
    contacts = relationship(
        "LeadContact",
        back_populates="lead",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        # The dedup guarantee: one master lead per company per tenant.
        UniqueConstraint(
            "tenant_id",
            "fingerprint",
            name="uq_leads_tenant_fingerprint",
        ),
        Index("idx_leads_tenant", "tenant_id"),
        # Hot UI query: a tenant's leads filtered by funnel status.
        Index("idx_leads_tenant_status", "tenant_id", "status"),
        Index("idx_leads_tenant_domain", "tenant_id", "company_domain"),
        Index("idx_leads_canonical", "canonical_url_id"),
        Index("idx_leads_last_seen", "tenant_id", "last_seen_at"),
        # Keep the JSONB long tail queryable as it grows.
        Index("idx_leads_signals_gin", "signals", postgresql_using="gin"),
        Index(
            "idx_leads_custom_fields_gin",
            "custom_fields",
            postgresql_using="gin",
        ),
    )


class LeadContact(Base):
    """An individual person belonging to a master Lead.

    Contacts attach to the **master** (not to a single run's observation) and
    are deduplicated by email, so a person found in multiple runs is one row
    whose ``last_seen_at`` is bumped, while a newly-appearing person is
    inserted. This is how "run 2 found an extra contact" is handled cleanly.
    """

    __tablename__ = "lead_contacts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuidv7()"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
    )

    full_name: Mapped[str | None] = mapped_column(Text)
    first_name: Mapped[str | None] = mapped_column(Text)
    last_name: Mapped[str | None] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(Text)
    seniority: Mapped[str | None] = mapped_column(Text)
    department: Mapped[str | None] = mapped_column(Text)

    email: Mapped[str | None] = mapped_column(Text)
    email_status: Mapped[ContactEmailStatusEnum] = mapped_column(
        SqlEnum(
            ContactEmailStatusEnum,
            name="contact_email_status",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=ContactEmailStatusEnum.UNVERIFIED,
    )
    phone: Mapped[str | None] = mapped_column(Text)
    linkedin_url: Mapped[str | None] = mapped_column(Text)

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    confidence_score: Mapped[float | None] = mapped_column(Float)

    attributes: Mapped[dict | None] = mapped_column(JSONB)

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    lead = relationship("Lead", back_populates="contacts")

    __table_args__ = (
        # Dedup the same person on a lead by email (only when an email exists).
        Index(
            "uq_lead_contacts_email",
            "lead_id",
            "email",
            unique=True,
            postgresql_where=text("email IS NOT NULL"),
        ),
        Index("idx_lead_contacts_tenant", "tenant_id"),
        Index("idx_lead_contacts_lead", "lead_id"),
        Index("idx_lead_contacts_email", "email"),
    )
