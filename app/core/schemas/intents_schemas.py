from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from dataclasses import dataclass
from uuid import UUID


class CreateIntentJobsRequest(BaseModel):
    request_name: str
    original_query: str
    schedule_expression: str = "0 */6 * * *"
    job_config_id: UUID | None = None


class CreateIntentJobsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    request_name: str
    status: str
    schedule_expression: str
    job_config_id: UUID | None = None
    created_at: datetime
    created_by: UUID


@dataclass
class IntentJobCreate:
    tenant_id: UUID
    created_by: UUID
    request_name: str
    original_query: str
    schedule_expression: str = "0 */6 * * *"
    next_run_at: datetime | None = None
    selected_config_version_id: UUID | None = None
