from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from dataclasses import dataclass
from uuid import UUID


class CreateJobConfigRequest(BaseModel):
    tenant_id: UUID
    created_by: UUID
    request_name: str
    original_query: str
    schedule_expression: str = "0 */6 * * *"


class CreateJobConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    request_name: str
    status: str
    schedule_expression: str
    created_at: datetime
    created_by: UUID
