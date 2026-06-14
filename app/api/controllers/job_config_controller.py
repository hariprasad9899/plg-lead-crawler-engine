from uuid import UUID
from fastapi import APIRouter, Depends
from app.core.utils.env_config import Settings
from app.core.schemas.job_config_schemas import (
    CreateJobConfigRequest,
    CreateJobConfigResponse,
    UpdateJobConfigRequest,
    UpdateJobConfigResponse,
    CreateJobConfigVersionRequest,
    CreateJobConfigVersionResponse,
)
from app.core.services.job_config_services import JobConfigService
from app.core.dependencies.job_config_dependencies import get_job_config_service
from app.auth.schemas import AuthContext
from app.auth.dependencies import get_auth_context

router = APIRouter(prefix="/job-config", tags=["JobConfig"])
settings = Settings()


@router.post("", response_model=CreateJobConfigResponse)
def create_job_config(
    req_data: CreateJobConfigRequest,
    auth: AuthContext = Depends(get_auth_context),
    service: JobConfigService = Depends(get_job_config_service),
):
    tenant_id = auth.tenant_id
    user_id = auth.user_id
    return service.create_job_config(
        tenant_id=tenant_id, user_id=user_id, data=req_data
    )


@router.patch("/{job_config_id}", response_model=UpdateJobConfigResponse)
def update_job_config(
    job_config_id: UUID,
    req_data: UpdateJobConfigRequest,
    auth: AuthContext = Depends(get_auth_context),
    service: JobConfigService = Depends(get_job_config_service),
):
    tenant_id = auth.tenant_id
    user_id = auth.user_id
    return service.update_job_config(
        job_config_id=job_config_id, tenant_id=tenant_id, user_id=user_id, data=req_data
    )


@router.post("/versions", response_model=CreateJobConfigVersionResponse)
def create_job_config_version(
    req_data: CreateJobConfigVersionRequest,
    auth: AuthContext = Depends(get_auth_context),
    service: JobConfigService = Depends(get_job_config_service),
):
    tenant_id = auth.tenant_id
    user_id = auth.user_id
    return service.create_job_config_version(
        tenant_id=tenant_id, user_id=user_id, data=req_data
    )
