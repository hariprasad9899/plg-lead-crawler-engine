from app.core.exceptions.base import AppException
from app.core.exceptions.error_catalog import (
    JOB_CONFIG_VERSION_NOT_FOUND,
    INTENT_JOB_NOT_FOUND,
)
from app.infrastructure.database.repositories.intent_repository import IntentRepo
from app.infrastructure.database.repositories.job_config_repository import JobConfigRepo
from app.core.schemas.intents_schemas import (
    IntentJobCreate,
    CreateIntentJobsRequest,
    CreateIntentJobsResponse,
    UpdatedIntentJobConfigVersion,
    UpdatedIntentJobConfigVersionResponse,
)
from app.core.config.constants import APP_CONSTANTS
from app.core.utils.crontier import compute_timestamp_from_cron
from uuid import UUID
from app.core.utils.response import success_response


class IntentService:
    def __init__(self, intent_repo: IntentRepo, job_config_repo: JobConfigRepo):
        self.intent_repo = intent_repo
        self.job_config_repo = job_config_repo

    def create_intent(
        self, tenant_id: UUID, user_id: UUID, data: CreateIntentJobsRequest
    ) -> CreateIntentJobsResponse:
        try:
            schedule_expression = (
                data.schedule_expression or APP_CONSTANTS.DEFAULT_SCHEDULE_EXP
            )
            next_run_at = compute_timestamp_from_cron(
                cron_expression=schedule_expression
            )
            intent_job_data = IntentJobCreate(
                tenant_id=tenant_id,
                created_by=user_id,
                request_name=data.request_name,
                original_query=data.original_query,
                schedule_expression=schedule_expression,
                next_run_at=next_run_at,
                current_config_version_id=data.job_config_id,
            )
            intent_job = self.intent_repo.create_intent(data=intent_job_data)
            self.intent_repo.db.commit()
            res_data = {
                "id": intent_job.id,
                "tenant_id": intent_job.tenant_id,
                "request_name": intent_job.request_name,
                "status": intent_job.status,
                "schedule_expression": intent_job.schedule_expression,
                "job_config_id": intent_job.current_config_version_id,
                "created_at": intent_job.created_at,
                "created_by": intent_job.created_by,
            }
            return success_response(res_data)
        except Exception:
            self.intent_repo.db.rollback()
            raise

    def updated_intent_config_version(
        self,
        tenant_id: UUID,
        user_id: UUID,
        intent_job_id: UUID,
        data: UpdatedIntentJobConfigVersion,
    ) -> UpdatedIntentJobConfigVersionResponse:
        try:
            job_config_version = self.job_config_repo.get_job_config_version(
                job_config_version_id=data.job_config_version_id, tenant_id=tenant_id
            )
            if data.job_config_version_id and not job_config_version:
                raise AppException(JOB_CONFIG_VERSION_NOT_FOUND)

            intent_job = self.intent_repo.updated_config_version(
                tenant_id=tenant_id,
                user_id=user_id,
                intent_job_id=intent_job_id,
                config_version_id=data.job_config_version_id,
            )
            self.intent_repo.db.commit()
            res_data = {
                "id": str(intent_job.id),
                "tenant_id": str(intent_job.tenant_id),
                "request_name": intent_job.request_name,
                "status": intent_job.status,
                "job_config_id": intent_job.current_config_version_id,
                "updated_at": intent_job.updated_at,
                "updated_by": intent_job.updated_by,
            }
            return success_response(res_data)
        except Exception:
            self.intent_repo.db.rollback()
            raise

    def get_intent(
        self, tenant_id: UUID, intent_job_id: UUID
    ) -> CreateIntentJobsResponse:
        try:
            intent_job = self.intent_repo.get_intent(
                intent_job_id=intent_job_id, tenant_id=tenant_id
            )
            if not intent_job:
                raise AppException(INTENT_JOB_NOT_FOUND)

            res_data = {
                "id": intent_job.id,
                "tenant_id": intent_job.tenant_id,
                "request_name": intent_job.request_name,
                "status": intent_job.status,
                "schedule_expression": intent_job.schedule_expression,
                "job_config_id": intent_job.current_config_version_id,
                "created_at": intent_job.created_at,
                "created_by": intent_job.created_by,
            }
            return success_response(res_data)
        except Exception:
            raise
