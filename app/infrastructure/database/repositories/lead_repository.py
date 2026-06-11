from typing import Any
from uuid import UUID

from sqlalchemy import func, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session as SQLAlchemySession

from app.infrastructure.database.models.crawled_lead import CrawledLead
from app.infrastructure.database.models.lead import Lead, LeadContact


# Fields on the master Lead that a new observation is allowed to merge into.
# Rule applied below: "last-write-wins, but never overwrite a known value with
# NULL" (i.e. coalesce(new, existing)). NOTE this deliberately EXCLUDES the
# qualification lifecycle (status, qualification_score, enrichment_status,
# synced_to_crm, ...) — those are set by humans / downstream jobs and must not
# be clobbered by a re-crawl.
LEAD_MERGE_FIELDS = (
    "canonical_url_id",
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
    "primary_contact_name",
    "primary_contact_title",
    "primary_contact_email",
    "primary_contact_phone",
    "firmographics",
    "signals",
    "enrichment",
    "custom_fields",
)

# Per-contact fields merged on conflict (same last-write-no-null rule).
CONTACT_MERGE_FIELDS = (
    "full_name",
    "first_name",
    "last_name",
    "title",
    "seniority",
    "department",
    "email_status",
    "phone",
    "linkedin_url",
    "is_primary",
    "confidence_score",
    "attributes",
)


class LeadRepository:
    """Persistence for the master/observation lead model.

    All methods ``flush`` (so generated ids are available) but do NOT commit —
    the caller owns the transaction boundary, matching the existing repo style.
    """

    def __init__(self, db: SQLAlchemySession):
        self.db = db

    def upsert_master_lead(
        self,
        *,
        tenant_id: UUID,
        fingerprint: str,
        values: dict[str, Any],
    ) -> UUID:
        """Insert a new master Lead or merge into the existing one.

        Deduped by ``(tenant_id, fingerprint)``. On conflict, mergeable fields
        follow last-write-no-null, ``last_seen_at`` is bumped and ``times_seen``
        is incremented. Returns the master lead id.
        """
        insert_values = {
            "tenant_id": tenant_id,
            "fingerprint": fingerprint,
            **values,
        }
        stmt = pg_insert(Lead).values(**insert_values)

        update_set: dict[str, Any] = {
            name: func.coalesce(
                getattr(stmt.excluded, name),
                getattr(Lead, name),
            )
            for name in LEAD_MERGE_FIELDS
            if name in values
        }
        update_set["last_seen_at"] = func.now()
        update_set["times_seen"] = Lead.times_seen + 1
        update_set["updated_at"] = func.now()

        stmt = stmt.on_conflict_do_update(
            constraint="uq_leads_tenant_fingerprint",
            set_=update_set,
        ).returning(Lead.id)

        lead_id = self.db.execute(stmt).scalar_one()
        self.db.flush()
        return lead_id

    def add_observation(
        self,
        *,
        lead_id: UUID,
        values: dict[str, Any],
    ) -> UUID:
        """Record the per-run snapshot. Upserts on ``(job_run_id,
        canonical_url_id)`` so re-extracting the same page in a run refreshes
        rather than duplicates. Returns the observation id.
        """
        insert_values = {"lead_id": lead_id, **values}
        stmt = pg_insert(CrawledLead).values(**insert_values)

        refresh = (
            "company_name",
            "company_domain",
            "industry",
            "employee_count",
            "confidence_score",
            "extraction_method",
            "raw_extraction",
            "signals",
            "lead_type",
            "source",
            "crawled_page_id",
        )
        update_set = {
            name: getattr(stmt.excluded, name)
            for name in refresh
            if name in insert_values
        }
        stmt = stmt.on_conflict_do_update(
            constraint="uq_crawled_leads_run_canonical",
            set_=update_set,
        ).returning(CrawledLead.id)

        observation_id = self.db.execute(stmt).scalar_one()
        self.db.flush()
        return observation_id

    def upsert_contact(
        self,
        *,
        tenant_id: UUID,
        lead_id: UUID,
        values: dict[str, Any],
    ) -> None:
        """Add or update one contact on a master lead.

        When an email is present, dedupe on ``(lead_id, email)`` (bump
        ``last_seen_at``, merge fields). Without an email we cannot reliably
        dedupe, so the contact is simply appended.
        """
        insert_values = {
            "tenant_id": tenant_id,
            "lead_id": lead_id,
            **values,
        }

        if not values.get("email"):
            self.db.add(LeadContact(**insert_values))
            self.db.flush()
            return

        stmt = pg_insert(LeadContact).values(**insert_values)
        update_set: dict[str, Any] = {
            name: func.coalesce(
                getattr(stmt.excluded, name),
                getattr(LeadContact, name),
            )
            for name in CONTACT_MERGE_FIELDS
            if name in values
        }
        update_set["last_seen_at"] = func.now()

        stmt = stmt.on_conflict_do_update(
            index_elements=["lead_id", "email"],
            index_where=text("email IS NOT NULL"),
            set_=update_set,
        )
        self.db.execute(stmt)
        self.db.flush()
