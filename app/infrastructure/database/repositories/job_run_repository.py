from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.orm import Session as SQLAlchemySession
from app.infrastructure.database.models.job_runs import JobRun, RunStatusEnum


class JobRunRepo:
    def __init__(self, db: SQLAlchemySession):
        self.db = db

    def create_job_run(
        self,
        intent_job_id: UUID,
        job_config_version_id: UUID,
        tenant_id: UUID,
        created_by: UUID,
    ):
        job_run = JobRun(
            intent_job_id=intent_job_id,
            job_config_version_id=job_config_version_id,
            tenant_id=tenant_id,
            created_by=created_by,
        )
        self.db.add(job_run)
        self.db.flush()
        return job_run

    def get_by_id(self, job_run_id: UUID) -> JobRun | None:
        return self.db.query(JobRun).filter(JobRun.id == job_run_id).first()

    def mark_running(self, job_run: JobRun) -> JobRun:
        job_run.status = RunStatusEnum.RUNNING
        job_run.started_at = datetime.now(timezone.utc)
        self.db.flush()
        return job_run

    def mark_completed(self, job_run: JobRun, seed_urls_count: int = 0) -> JobRun:
        job_run.status = RunStatusEnum.COMPLETED
        job_run.completed_at = datetime.now(timezone.utc)
        job_run.seed_urls_count = seed_urls_count
        self.db.flush()
        return job_run

    def mark_failed(self, job_run: JobRun) -> JobRun:
        job_run.status = RunStatusEnum.FAILED
        job_run.completed_at = datetime.now(timezone.utc)
        self.db.flush()
        return job_run
