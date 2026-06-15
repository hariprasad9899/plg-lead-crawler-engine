from uuid import UUID

from app.core.dependencies.search_generation_dependencies import (
    build_search_generation_service,
)
from app.core.logger.logger import get_logger
from app.core.queue.celery_app import celery_app
from app.core.schemas.intents_schemas import IntentGenerationInput

logger = get_logger(__name__)


@celery_app.task(
    name="search_worker.generate_search_queries",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    acks_late=True,
)
def generate_search_queries(self, job_run_id: str, intent_gen_input: dict):
    """
    Generate and persist search queries for a job run.

    ``intent_gen_input`` arrives as a plain dict (Celery JSON payload) and is
    rehydrated into :class:`IntentGenerationInput` before processing.
    """
    logger.info(f"Received search-query generation task for job_run={job_run_id}")

    intent_input = IntentGenerationInput(**intent_gen_input)
    service = build_search_generation_service()

    try:
        created = service.generate_for_job_run(
            job_run_id=UUID(job_run_id),
            intent_input=intent_input,
        )
        logger.info(f"Generated {len(created)} search queries for job_run={job_run_id}")
        return {"job_run_id": job_run_id, "queries_generated": len(created)}
    except Exception as exc:
        # The service has already marked the run FAILED; retry transient errors.
        logger.error(f"Task failed for job_run={job_run_id}: {exc}")
        raise self.retry(exc=exc)
