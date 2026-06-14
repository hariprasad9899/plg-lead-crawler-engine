from uuid import UUID
from app.core.exceptions.base import AppException
from app.core.exceptions.error_catalog import (
    JOB_CONFIG_NOT_FOUND,
    JOB_CONFIG_VERSION_NOT_FOUND,
)
from app.infrastructure.database.repositories.job_config_repository import JobConfigRepo
from app.core.schemas.job_config_schemas import (
    CreateJobConfigResponse,
    JobConfig,
    UpdateJobConfigRequest,
    UpdateJobConfigResponse,
    JobConfigVersion,
    CreateJobConfigVersionResponse,
)
from app.core.utils.response import success_response


class JobConfigService:
    def __init__(self, repo: JobConfigRepo):
        self.repo = repo

    def update_job_config(
        self,
        job_config_id: UUID,
        tenant_id: UUID,
        user_id: UUID,
        data: UpdateJobConfigRequest,
    ) -> UpdateJobConfigResponse:
        try:
            job_config = self.repo.get_job_config(
                job_config_id=job_config_id, tenant_id=tenant_id
            )
            if job_config is None:
                raise AppException(JOB_CONFIG_NOT_FOUND)

            job_config = self.repo.update_job_config(
                job_config=job_config,
                updated_by=user_id,
                name=data.name,
                description=data.description,
            )
            self.repo.db.commit()
            self.repo.db.refresh(job_config)
            return success_response(
                {
                    "id": str(job_config.id),
                    "tenant_id": str(job_config.tenant_id),
                    "name": job_config.name,
                    "description": job_config.description,
                    "created_by": str(job_config.created_by),
                    "updated_by": (
                        str(job_config.updated_by) if job_config.updated_by else None
                    ),
                    "created_at": job_config.created_at,
                    "updated_at": job_config.updated_at,
                }
            )
        except Exception:
            self.repo.db.rollback()
            raise

    def create_job_config(
        self, tenant_id: UUID, user_id: UUID, data: JobConfig
    ) -> CreateJobConfigResponse:
        try:
            job_config, job_config_version = self.repo.create_job_config(
                data=data, user_id=user_id, tenant_id=tenant_id
            )
            self.repo.db.commit()
            job_config_data = {
                "id": str(job_config.id),
                "tenant_id": str(job_config.tenant_id),
                "name": job_config.name,
                "description": job_config.description,
                "created_by": str(job_config.created_by),
                "current_version": {
                    "id": str(job_config_version.id),
                    "version_number": job_config_version.version_number,
                    "config": job_config_version.config,
                    "created_at": job_config_version.created_at,
                    "created_by": str(job_config.created_by),
                },
            }
            return success_response(job_config_data)
        except Exception:
            self.repo.db.rollback()
            raise

    def create_job_config_version(
        self, tenant_id: UUID, user_id: UUID, data: JobConfigVersion
    ) -> CreateJobConfigVersionResponse:
        try:
            job_config = self.repo.get_job_config(
                job_config_id=data.job_config_id, tenant_id=tenant_id
            )
            if not job_config:
                raise AppException(JOB_CONFIG_NOT_FOUND)
            job_config_version = self.repo.create_job_config_version(
                tenant_id=tenant_id, user_id=user_id, data=data
            )
            self.repo.db.commit()
            job_config_data = {
                "id": str(job_config.id),
                "tenant_id": str(job_config.tenant_id),
                "name": job_config.name,
                "description": job_config.description,
                "created_by": str(job_config.created_by),
                "current_version": {
                    "id": str(job_config_version.id),
                    "version_number": job_config_version.version_number,
                    "config": job_config_version.config,
                    "created_at": job_config_version.created_at,
                    "created_by": str(job_config.created_by),
                },
            }
            return success_response(job_config_data)
        except Exception:
            self.repo.db.rollback()
            raise

    def get_job_config_version(self, job_config_version_id: UUID, tenant_id: UUID):
        job_config_version = self.repo.get_job_config_version(
            job_config_version_id=job_config_version_id, tenant_id=tenant_id
        )
        if not job_config_version:
            raise AppException(JOB_CONFIG_VERSION_NOT_FOUND)
        return job_config_version
