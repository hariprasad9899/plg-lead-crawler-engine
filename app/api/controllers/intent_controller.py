from fastapi import APIRouter, Depends, BackgroundTasks, Request, Response
from app.core.utils.response import success_response
from app.core.utils.env_config import Settings
from app.core.schemas.intents_schemas import (
    CreateIntentJobsRequest,
    CreateIntentJobsResponse,
)
from app.core.services.intent_services import IntentService
from app.core.dependencies.intent_dependencies import get_intent_service
from app.auth.dependencies import get_auth_context
from app.auth.schemas import AuthContext

router = APIRouter(prefix="/intents", tags=["Intents"])
settings = Settings()


@router.post("", response_model=CreateIntentJobsResponse)
def create_intent_jobs(
    req_data: CreateIntentJobsRequest,
    auth: AuthContext = Depends(get_auth_context),
    service: IntentService = Depends(get_intent_service),
):
    tenant_id = auth.tenant_id
    user_id = auth.user_id
    return service.create_intent(tenant_id=tenant_id, user_id=user_id, data=req_data)
