from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.infrastructure.database.models.lead import (
    ContactEmailStatusEnum,
    LeadSourceEnum,
    LeadTypeEnum,
)


class ExtractedContact(BaseModel):
    """A single person extracted from a crawled page."""

    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    seniority: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    email_status: ContactEmailStatusEnum = ContactEmailStatusEnum.UNVERIFIED
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    is_primary: bool = False
    confidence_score: Optional[float] = None
    attributes: Optional[dict[str, Any]] = None


class ExtractedLeadData(BaseModel):
    """The payload produced by the extraction step for one crawled page.

    This is the input to :class:`LeadIngestionService`, which deduplicates it
    into the master ``leads`` table and records the per-run observation in
    ``crawled_leads``.
    """

    # ---- Provenance (required to attribute the observation) ----
    tenant_id: UUID
    job_run_id: UUID
    canonical_url_id: UUID
    crawled_page_id: Optional[UUID] = None

    lead_type: LeadTypeEnum = LeadTypeEnum.COMPANY
    source: LeadSourceEnum = LeadSourceEnum.CRAWL

    # Optional explicit dedup key; if omitted it is derived from domain/email.
    fingerprint: Optional[str] = None

    # ---- Firmographics ----
    company_name: Optional[str] = None
    company_domain: Optional[str] = None
    company_website: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    employee_range: Optional[str] = None
    revenue_range: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    linkedin_url: Optional[str] = None

    # ---- Quality / provenance of this extraction ----
    confidence_score: Optional[float] = None
    extraction_method: Optional[str] = None

    # ---- Expandable long tail ----
    firmographics: Optional[dict[str, Any]] = None
    signals: Optional[dict[str, Any]] = None
    enrichment: Optional[dict[str, Any]] = None
    custom_fields: Optional[dict[str, Any]] = None
    raw_extraction: Optional[dict[str, Any]] = None

    # ---- People found on the page ----
    contacts: list[ExtractedContact] = Field(default_factory=list)
