from fastapi import APIRouter, Depends
from uuid import UUID
from app.core.utils.response import success_response
from app.core.utils.env_config import Settings
from app.core.schemas.intents_schemas import (
    CreateIntentJobsRequest,
    CreateIntentJobsResponse,
    UpdatedIntentJobConfigVersion,
    UpdatedIntentJobConfigVersionResponse,
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


@router.get("/{intent_id}", response_model=CreateIntentJobsResponse)
def get_intent(
    intent_id: UUID,
    auth: AuthContext = Depends(get_auth_context),
    service: IntentService = Depends(get_intent_service),
):
    tenant_id = auth.tenant_id
    return service.get_intent(tenant_id=tenant_id, intent_job_id=intent_id)


@router.patch(
    "/{intent_id}/config-version", response_model=UpdatedIntentJobConfigVersionResponse
)
def update_config_version(
    intent_id: UUID,
    req_data: UpdatedIntentJobConfigVersion,
    auth: AuthContext = Depends(get_auth_context),
    service: IntentService = Depends(get_intent_service),
):
    tenant_id = auth.tenant_id
    user_id = auth.user_id
    return service.updated_intent_config_version(
        tenant_id=tenant_id, user_id=user_id, intent_job_id=intent_id, data=req_data
    )
