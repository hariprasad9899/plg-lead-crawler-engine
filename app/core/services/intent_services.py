from app.core.exceptions.base import AppException
from app.infrastructure.database.repositories.intent_repository import IntentRepo
from app.core.schemas.intents_schemas import (
    IntentJobCreate,
    CreateIntentJobsRequest,
    CreateIntentJobsResponse,
)
from dataclasses import asdict
from app.core.config.constants import APP_CONSTANTS
from app.core.utils.crontier import compute_timestamp_from_cron


class IntentService:
    def __init__(self, intent_repo: IntentRepo):
        self.intent_repo = intent_repo

    def create_intent(self, data: CreateIntentJobsRequest) -> CreateIntentJobsResponse:
        try:
            intent_data = data.model_dump()
            schedule_expression = intent_data.get(
                "schedule_expression", APP_CONSTANTS.DEFAULT_SCHEDULE_EXP
            )
            next_run_at = compute_timestamp_from_cron(
                cron_expression=schedule_expression
            )
            intent_data["next_run_at"] = next_run_at
            intent_job_data = IntentJobCreate(**intent_data)
            intent_job = self.intent_repo.create_intent(data=intent_job_data)
            self.intent_repo.db.commit()
            res_data = {
                "id": intent_job.id,
                "tenant_id": intent_job.tenant_id,
                "request_name": intent_job.request_name,
                "status": intent_job.status,
                "schedule_expression": intent_job.schedule_expression,
                "created_at": intent_job.created_at,
                "created_by": intent_job.created_by,
            }
            return res_data
        except Exception:
            self.intent_repo.db.rollback()
            raise
