from app.core.exceptions.base import AppException
from app.core.exceptions.error_catalog import INTENT_JOB_NOT_FOUND
from app.infrastructure.database.repositories.intent_repository import IntentRepo
from app.core.services.job_config_services import JobConfigService
from app.core.services.job_run_service import JobRunService
from app.core.schemas.intents_schemas import (
    IntentJobCreate,
    CreateIntentJobsRequest,
    CreateIntentJobsResponse,
    UpdatedIntentJobConfigVersion,
    UpdatedIntentJobConfigVersionResponse,
    IntentGenerationInput,
)
from app.core.config.constants import APP_CONSTANTS
from app.core.utils.crontier import compute_timestamp_from_cron
from uuid import UUID
from app.core.utils.response import success_response
from app.core.ai.intent.intent_normalizer import IntentNormalizer
from app.core.logger import get_logger
from app.core.exceptions.error_catalog import JOB_CONFIG_NOT_FOUND
from dataclasses import asdict

logger = get_logger()


class IntentService:
    def __init__(
        self,
        intent_repo: IntentRepo,
        job_config_service: JobConfigService,
        job_run_service: JobRunService,
    ):
        self.intent_repo = intent_repo
        self.job_config_service = job_config_service
        self.job_run_service = job_run_service
        self.intent_normalizer = IntentNormalizer()

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
            logger.info("Creating Intent Job")
            intent_job = self.intent_repo.create_intent(data=intent_job_data)

            logger.info("Creating Job Run")
            job_run = self.job_run_service.create_job_run(
                intent_job_id=intent_job.id,
                job_config_version_id=data.job_config_id,
                tenant_id=tenant_id,
                created_by=user_id,
            )

            job_config_version = self.job_config_service.get_job_config_version(
                job_config_version_id=intent_job.current_config_version_id,
                tenant_id=tenant_id,
            )
            if not job_config_version:
                raise AppException(JOB_CONFIG_NOT_FOUND)

            job_config = job_config_version.job_config
            if not job_config:
                raise AppException(JOB_CONFIG_NOT_FOUND)

            intent_generation_input = IntentGenerationInput(
                request_name=intent_job.request_name,
                original_query=intent_job.original_query,
                config=job_config_version.config,
                config_name=job_config.name,
                config_description=job_config.description,
            )

            logger.info("Store Intent Embeddings")
            from app.search_worker.task import store_intent_embeddings

            store_intent_embeddings.delay(
                tenant_id=tenant_id,
                intent_id=intent_job.id,
                intent_request_name=intent_job.request_name,
                intent_original_query=intent_job.original_query,
            )

            logger.info("Triggering Job Run")
            from app.search_worker.task import generate_search_queries

            generate_search_queries.delay(
                str(job_run.id), asdict(intent_generation_input)
            )

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
            if data.job_config_version_id:
                job_config_version = self.job_config_service.get_job_config_version(
                    job_config_version_id=data.job_config_version_id,
                    tenant_id=tenant_id,
                )

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

    def store_intent_embedding(
        self, tenant_id: UUID, intent_id: UUID, intent_embedding: list[float]
    ):
        try:
            intent_job = self.intent_repo.get_intent(
                intent_job_id=intent_id, tenant_id=tenant_id
            )
            if not intent_job:
                raise AppException(INTENT_JOB_NOT_FOUND)
            intent_job.intent_embedding = intent_embedding
            self.intent_repo.db.flush()
            self.intent_repo.db.commit()
        except Exception:
            self.intent_repo.db.rollback()
            raise
