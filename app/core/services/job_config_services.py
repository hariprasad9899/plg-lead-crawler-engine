from app.core.exceptions.base import AppException
from app.infrastructure.database.repositories.job_config_repository import JobConfigRepo
from app.core.schemas.job_config_schemas import (
    CreateJobConfigResponse,
    CreateJobConfigRequest,
)


class JobConfigService:
    def __init__(self, repo: JobConfigRepo):
        self.repo = repo

    def create_job_config(
        self, data: CreateJobConfigRequest
    ) -> CreateJobConfigResponse:
        try:
            return None
        except Exception:
            self.intent_repo.db.rollback()
            raise
