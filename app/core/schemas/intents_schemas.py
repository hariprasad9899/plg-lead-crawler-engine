from pydantic import BaseModel,ConfigDict
from typing import Optional
from datetime import datetime
from dataclasses import dataclass
from uuid import UUID

class CreateIntentJobsRequest(BaseModel):
    tenant_id: str
    created_by: str
    request_name: str
    original_query: str
    product_name: str
    product_description: str
    target_industries: list[str]
    target_countries: list[str]
    min_company_size: Optional[int] = None
    max_company_size: Optional[int] = None
    target_personas: Optional[list[str]] = None
    target_technologies: Optional[list[str]] = None
    excluded_technologies: Optional[list[str]] = None
    buying_signals: Optional[list[str]] = None
    negative_signals: Optional[list[str]] = None
    signal_priority_weights: Optional[dict[str, int]] = None
    schedule_type: str = "cron"
    schedule_expression: str = "0 */6 * * *"
    lead_score_threshold: int
    max_urls_per_run: int


class CreateIntentJobsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    request_name: str
    status: str
    schedule_type: str
    schedule_expression: str
    lead_score_threshold: int
    max_urls_per_run: int
    total_seed_urls: int
    total_processed_urls: int
    total_qualified_leads: int
    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


@dataclass
class IntentJobCreate:
    model_config = ConfigDict(extra="ignore") 
    tenant_id: str
    created_by: str
    request_name: str
    original_query: str
    product_name: str
    product_description: str
    target_industries: list[str]
    target_countries: list[str]
    lead_score_threshold: int
    max_urls_per_run: int
    min_company_size: Optional[int] = None
    max_company_size: Optional[int] = None
    target_personas: Optional[list[str]] = None
    target_technologies: Optional[list[str]] = None
    excluded_technologies: Optional[list[str]] = None
    buying_signals: Optional[list[str]] = None
    negative_signals: Optional[list[str]] = None
    signal_priority_weights: Optional[dict[str, int]] = None
    schedule_type: str = "cron"
    schedule_expression: str = "0 */6 * * *"