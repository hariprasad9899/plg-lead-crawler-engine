from uuid import UUID
from app.infrastructure.database.repositories.job_run_repository import JobRunRepo


class JobRunService:
    def __init__(self, job_run_repo: JobRunRepo):
        self.job_run_repo = job_run_repo

    def create_job_run(
        self,
        intent_job_id: UUID,
        job_config_version_id: UUID,
        tenant_id: UUID,
        created_by: UUID,
    ):
        job_run = self.job_run_repo.create_job_run(
            intent_job_id=intent_job_id,
            job_config_version_id=job_config_version_id,
            tenant_id=tenant_id,
            created_by=created_by,
        )
        return job_run
