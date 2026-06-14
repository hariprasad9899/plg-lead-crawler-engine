from sqlalchemy.orm import Session as SQLAlchemySession
from pydantic import EmailStr
from app.infrastructure.database.models.intent_job import IntentJob
from app.core.schemas.intents_schemas import IntentJobCreate
from typing import Optional
from dataclasses import asdict
from uuid import UUID


class IntentRepo:
    def __init__(self, db: SQLAlchemySession):
        self.db = db

    def create_intent(self, data: IntentJobCreate):
        db_obj = IntentJob(**asdict(data))
        self.db.add(db_obj)
        self.db.flush()
        return db_obj

    def get_intent(self, intent_job_id: UUID, tenant_id: UUID) -> IntentJob | None:
        return (
            self.db.query(IntentJob)
            .filter(IntentJob.id == intent_job_id, IntentJob.tenant_id == tenant_id)
            .first()
        )

    def updated_config_version(
        self,
        tenant_id: UUID,
        user_id: UUID,
        intent_job_id: UUID,
        config_version_id: UUID,
    ):
        intent_job = (
            self.db.query(IntentJob)
            .filter(IntentJob.tenant_id == tenant_id, IntentJob.id == intent_job_id)
            .first()
        )
        intent_job.current_config_version_id = config_version_id
        intent_job.updated_by = user_id
        self.db.flush()
        return intent_job
