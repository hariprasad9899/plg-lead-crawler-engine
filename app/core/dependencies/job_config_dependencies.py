from fastapi import Depends
from app.infrastructure.database.sessions.session import get_db
from app.infrastructure.database.repositories.job_config_repository import IntentRepo
from app.core.services.job_config_services import JobConfigService


def get_job_config_service(db=Depends(get_db)):
    intent_repo = IntentRepo(db=db)
    return JobConfigService(intent_repo=intent_repo)
