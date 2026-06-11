from fastapi import APIRouter, Depends, BackgroundTasks, Request, Response
from app.core.utils.response import success_response
from app.core.utils.env_config import Settings
from app.core.schemas.job_config_schemas import (
    CreateJobConfigRequest,
    CreateJobConfigResponse,
)
from app.core.services.job_config_services import JobConfigService
from app.core.dependencies.job_config_dependencies import get_job_config_service

router = APIRouter(prefix="/intents", tags=["Intents"])
settings = Settings()


@router.post("/job-config", response_model=CreateJobConfigResponse)
def create_job_config(
    req_data: CreateJobConfigRequest,
    service: JobConfigService = Depends(get_job_config_service),
):
    return service.create_job_config(data=req_data)
