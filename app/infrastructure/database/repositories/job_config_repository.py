from sqlalchemy.orm import Session as SQLAlchemySession
from pydantic import EmailStr
from app.infrastructure.database.models.job_config import JobConfigModel
from app.infrastructure.database.models.job_config_versions import JobConfigVersionModel
from app.core.schemas.job_config_schemas import JobConfig


class JobConfigRepo:
    def __init__(self, db: SQLAlchemySession):
        self.db = db

    def create_job_config(self, data: JobConfig):
        job_config = JobConfigModel(
            tenant_id=data.tenant_id,
            created_by=data.created_by,
            name=data.name,
            description=data.description,
        )
        self.db.add(job_config)
        self.db.flush()
        job_config_version = JobConfigVersionModel(
            tenant_id=data.tenant_id,
            job_config_id=job_config.id,
            version_number=1,
            config=data.config,
        )
        self.db.add(job_config_version)
        self.db.flush()
        job_config.current_version_id = job_config_version.id
        self.db.flush()
        return [job_config, job_config_version]
