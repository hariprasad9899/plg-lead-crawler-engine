from pydantic import BaseModel, ConfigDict
from typing import Any
from datetime import datetime
from uuid import UUID
from dataclasses import dataclass


class CreateJobConfigRequest(BaseModel):
    tenant_id: UUID
    created_by: UUID
    name: str
    description: str
    config: dict[str, Any]


class JobConfigVersionResponse(BaseModel):
    id: UUID
    version_number: int
    config: dict[str, Any]
    created_at: datetime


class CreateJobConfigResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    description: str
    created_by: UUID
    current_version: JobConfigVersionResponse
    created_at: datetime
    updated_at: datetime


@dataclass
class JobConfig:
    tenant_id: UUID
    created_by: UUID
    name: str
    description: str
    config: dict[str, Any]
