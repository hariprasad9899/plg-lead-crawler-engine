from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from typing import Any
from datetime import datetime
from uuid import UUID
from dataclasses import dataclass

from app.core.exceptions.base import AppException
from app.core.exceptions.error_catalog import (
    FIELD_CANNOT_BE_BLANK,
    JOB_CONFIG_UPDATE_FIELDS_REQUIRED,
)


class CreateJobConfigRequest(BaseModel):
    tenant_id: UUID
    created_by: UUID
    name: str
    description: str
    config: dict[str, Any]


class UpdateJobConfigRequest(BaseModel):
    tenant_id: UUID
    updated_by: UUID
    name: str | None = None
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_not_blank(cls, value: str | None, info):
        if value is not None and not value.strip():
            raise AppException(
                FIELD_CANNOT_BE_BLANK, details={"field": info.field_name}
            )
        return value

    @model_validator(mode="after")
    def validate_update_fields(self):
        if self.name is None and self.description is None:
            raise AppException(JOB_CONFIG_UPDATE_FIELDS_REQUIRED)
        return self


class UpdateJobConfigResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    description: str | None
    created_by: UUID
    updated_by: UUID | None
    created_at: datetime
    updated_at: datetime


class JobConfigVersionResponse(BaseModel):
    id: UUID
    version_number: int
    config: dict[str, Any]
    created_at: datetime
    created_by: UUID
    updated_at: datetime
    updated_by: UUID


class CreateJobConfigResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    description: str
    created_by: UUID
    current_version: JobConfigVersionResponse
    created_at: datetime
    created_by: UUID
    updated_at: datetime
    updated_by: UUID


class CreateJobConfigVersionRequest(BaseModel):
    job_config_id: UUID
    created_by: UUID
    tenant_id: UUID
    config: dict[str, Any]

    @model_validator(mode="before")
    @classmethod
    def validate_required_fields(cls, data):
        if isinstance(data, dict):
            required_fields = ["job_config_id", "created_by", "tenant_id", "config"]
            for field in required_fields:
                if field not in data or not data[field]:
                    raise AppException(FIELD_CANNOT_BE_BLANK, details={"field": field})
        return data


class CreateJobConfigVersionResponse(BaseModel):
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


@dataclass
class JobConfigVersion:
    job_config_id: UUID
    tenant_id: UUID
    created_by: UUID
    config: dict[str, Any]
