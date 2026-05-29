from fastapi import APIRouter, Depends, BackgroundTasks, Request, Response
from app.core.utils.response import success_response
from app.core.utils.env_config import Settings
from app.core.schemas.intents_schemas import CreateIntentJobsRequest,CreateIntentJobsResponse

router = APIRouter(prefix="/intents", tags=["Intents"])
settings = Settings()

@router.post("/intent-jobs",response_model=CreateIntentJobsResponse)
def create_intent_jobs(request:CreateIntentJobsRequest):
    return {"he": []}