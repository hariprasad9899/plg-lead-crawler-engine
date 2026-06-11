from fastapi import APIRouter, Depends, BackgroundTasks, Request, Response
from app.core.utils.response import success_response
from app.core.utils.env_config import Settings
from app.core.schemas.intents_schemas import (
    CreateIntentJobsRequest,
    CreateIntentJobsResponse,
)
from app.core.services.intent_services import IntentService
from app.core.dependencies.intent_dependencies import get_intent_service

router = APIRouter(prefix="/intents", tags=["Intents"])
settings = Settings()


@router.post("/intent-jobs", response_model=CreateIntentJobsResponse)
def create_intent_jobs(
    req_data: CreateIntentJobsRequest,
    service: IntentService = Depends(get_intent_service),
):
    return service.create_intent(data=req_data)
