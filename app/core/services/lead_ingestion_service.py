from __future__ import annotations

import hashlib
import re
from uuid import UUID

from sqlalchemy.orm import Session as SQLAlchemySession

from app.core.schemas.lead_schemas import ExtractedContact, ExtractedLeadData
from app.infrastructure.database.repositories.lead_repository import (
    LeadRepository,
)

_SCHEME_RE = re.compile(r"^[a-z]+://")
_WWW_RE = re.compile(r"^www\.")


def normalize_domain(value: str | None) -> str | None:
    """Lowercase and strip scheme / www / path so the same site always maps
    to the same string (``HTTPS://www.CompanyA.com/about`` -> ``companya.com``).
    """
    if not value:
        return None
    v = value.strip().lower()
    v = _SCHEME_RE.sub("", v)
    v = v.split("/", 1)[0]
    v = _WWW_RE.sub("", v)
    return v or None


def compute_fingerprint(
    *,
    domain: str | None = None,
    email: str | None = None,
) -> str:
    """Stable dedup key for a lead.

    Prefers the normalized company domain; falls back to a normalized email.
    Returned as a hex SHA-256 so it is fixed-width and index-friendly. Raises
    if neither is available — a lead with no domain and no email cannot be
    deduplicated and the caller must decide how to handle it.
    """
    basis = normalize_domain(domain)
    if not basis and email:
        basis = email.strip().lower()
    if not basis:
        raise ValueError(
            "Cannot compute a lead fingerprint without a domain or email."
        )
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()


# Master-lead columns populated from the extracted payload. Lifecycle columns
# (status, qualification_score, enrichment_status, ...) are intentionally
# omitted so re-ingestion never overwrites them.
_MASTER_VALUE_FIELDS = (
    "canonical_url_id",
    "lead_type",
    "company_name",
    "company_domain",
    "company_website",
    "industry",
    "employee_count",
    "employee_range",
    "revenue_range",
    "country",
    "region",
    "city",
    "linkedin_url",
    "firmographics",
    "signals",
    "enrichment",
    "custom_fields",
)

_OBSERVATION_VALUE_FIELDS = (
    "tenant_id",
    "job_run_id",
    "canonical_url_id",
    "crawled_page_id",
    "lead_type",
    "source",
    "company_name",
    "company_domain",
    "industry",
    "employee_count",
    "confidence_score",
    "extraction_method",
    "raw_extraction",
    "signals",
)


class LeadIngestionService:
    """Turns one extracted page into a deduplicated lead + run observation.

    Flow per call:
      1. Resolve the fingerprint (explicit or derived from domain/email).
      2. Upsert the master ``leads`` row (dedup by tenant + fingerprint).
      3. Append the immutable per-run ``crawled_leads`` observation.
      4. Upsert each contact onto the master (dedup by email).

    The caller owns the transaction: call ``db.commit()`` after ingesting.
    """

    def __init__(self, db: SQLAlchemySession):
        self.db = db
        self.repo = LeadRepository(db)

    def ingest(self, data: ExtractedLeadData) -> UUID:
        primary_email = _primary_email(data.contacts)

        fingerprint = data.fingerprint or compute_fingerprint(
            domain=data.company_domain,
            email=primary_email,
        )

        master_values = {
            name: getattr(data, name)
            for name in _MASTER_VALUE_FIELDS
            if getattr(data, name) is not None
        }
        master_values.update(_primary_contact_cache(data.contacts))

        lead_id = self.repo.upsert_master_lead(
            tenant_id=data.tenant_id,
            fingerprint=fingerprint,
            values=master_values,
        )

        observation_values = {
            name: getattr(data, name)
            for name in _OBSERVATION_VALUE_FIELDS
            if getattr(data, name) is not None
        }
        self.repo.add_observation(
            lead_id=lead_id,
            values=observation_values,
        )

        for contact in data.contacts:
            self.repo.upsert_contact(
                tenant_id=data.tenant_id,
                lead_id=lead_id,
                values=_contact_values(contact),
            )

        return lead_id


def _primary_email(contacts: list[ExtractedContact]) -> str | None:
    primary = _primary_contact(contacts)
    return primary.email if primary else None


def _primary_contact(
    contacts: list[ExtractedContact],
) -> ExtractedContact | None:
    if not contacts:
        return None
    for c in contacts:
        if c.is_primary:
            return c
    return contacts[0]


def _primary_contact_cache(contacts: list[ExtractedContact]) -> dict:
    primary = _primary_contact(contacts)
    if not primary:
        return {}
    cache = {
        "primary_contact_name": primary.full_name,
        "primary_contact_title": primary.title,
        "primary_contact_email": primary.email,
        "primary_contact_phone": primary.phone,
    }
    return {k: v for k, v in cache.items() if v is not None}


def _contact_values(contact: ExtractedContact) -> dict:
    return contact.model_dump(exclude_none=True)
