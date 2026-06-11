from app.core.exceptions.base import AppException
from app.infrastructure.database.repositories.job_config_repository import JobConfigRepo
from app.core.schemas.job_config_schemas import (
    CreateJobConfigResponse,
    JobConfig,
)
from app.core.utils.response import success_response


class JobConfigService:
    def __init__(self, repo: JobConfigRepo):
        self.repo = repo

    def create_job_config(self, data: JobConfig) -> CreateJobConfigResponse:
        try:
            job_config, job_config_version = self.repo.create_job_config(data=data)
            self.repo.db.commit()
            job_config_data = {
                "id": str(job_config.id),
                "tenant_id": str(job_config.tenant_id),
                "name": job_config.name,
                "description": job_config.description,
                "created_by": job_config.created_by,
                "current_version": {
                    "id": str(job_config_version.id),
                    "version_number": job_config_version.version_number,
                    "config": job_config_version.config,
                    "created_at": job_config_version.created_at,
                },
            }
            return success_response(job_config_data)
        except Exception:
            self.repo.db.rollback()
            raise
