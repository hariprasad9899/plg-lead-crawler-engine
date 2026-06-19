from fastapi import Depends
from app.infrastructure.database.sessions.session import get_db
from app.infrastructure.database.repositories.intent_repository import IntentRepo
from app.infrastructure.database.repositories.job_config_repository import JobConfigRepo
from app.infrastructure.database.repositories.job_run_repository import JobRunRepo
from app.core.services.intent_services import IntentService
from app.core.services.job_config_services import JobConfigService
from app.core.services.job_run_service import JobRunService


def get_intent_service(db=Depends(get_db)):
    intent_repo = IntentRepo(db=db)
    job_config_repo = JobConfigRepo(db=db)
    job_run_repo = JobRunRepo(db=db)
    job_config_service = JobConfigService(repo=job_config_repo)
    job_run_service = JobRunService(job_run_repo=job_run_repo)

    return IntentService(
        intent_repo=intent_repo,
        job_config_service=job_config_service,
        job_run_service=job_run_service,
    )


def get_intent_service_for_celery():
    """For use in Celery tasks where FastAPI dependency injection isn't available."""
    from app.infrastructure.database.sessions.session import SessionLocal

    db = SessionLocal()
    try:
        intent_repo = IntentRepo(db=db)
        job_config_repo = JobConfigRepo(db=db)
        job_run_repo = JobRunRepo(db=db)
        job_config_service = JobConfigService(repo=job_config_repo)
        job_run_service = JobRunService(job_run_repo=job_run_repo)
        return IntentService(
            intent_repo=intent_repo,
            job_config_service=job_config_service,
            job_run_service=job_run_service,
        )
    finally:
        db.close()
