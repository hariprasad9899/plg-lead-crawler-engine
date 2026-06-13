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

router = APIRouter(prefix="/job-config", tags=["JobConfig"])
settings = Settings()


@router.post("", response_model=CreateJobConfigResponse)
def create_job_config(
    req_data: CreateJobConfigRequest,
    service: JobConfigService = Depends(get_job_config_service),
):
    return service.create_job_config(data=req_data)


@router.patch("/{job_config_id}", response_model=UpdateJobConfigResponse)
def update_job_config(
    job_config_id: UUID,
    req_data: UpdateJobConfigRequest,
    service: JobConfigService = Depends(get_job_config_service),
):

    return service.update_job_config(job_config_id=job_config_id, data=req_data)


@router.post("/versions", response_model=CreateJobConfigVersionRequest)
def creatr_job_config_version(
    req_data: CreateJobConfigVersionRequest,
    service: JobConfigService = Depends(get_job_config_service),
):
    return service.create_job_config_version(data=req_data)
