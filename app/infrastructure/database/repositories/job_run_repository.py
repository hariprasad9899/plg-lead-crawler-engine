from uuid import UUID
from sqlalchemy.orm import Session as SQLAlchemySession
from app.infrastructure.database.models.job_runs import JobRun


class JobRunRepo:
    def __init__(self, db: SQLAlchemySession):
        self.db = db

    def create_job_run(self, intent_job_id: UUID, job_config_version_id: UUID, tenant_id: UUID, created_by: UUID):
        job_run = JobRun(
            intent_job_id=intent_job_id,
            job_config_version_id=job_config_version_id,
            tenant_id=tenant_id,
            created_by=created_by,
        )
        self.db.add(job_run)
        self.db.flush()
        return job_run
