from uuid import UUID
from app.core.dependencies.search_generation_dependencies import (
    build_search_generation_service,
)
from app.core.dependencies.search_url_dependencies import build_search_url_service
from app.core.logger.logger import get_logger
from app.core.queue.celery_app import celery_app
from app.core.utils.env_config import settings
from app.core.schemas.intents_schemas import IntentGenerationInput
from app.infrastructure.llm.provider_factory import LLMProviderFactory
from app.core.dependencies.intent_dependencies import get_intent_service_for_celery

logger = get_logger(__name__)


@celery_app.task(
    name="search_worker.store_intent_embeddings",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    acks_late=True,
)
def store_intent_embeddings(
    self,
    tenant_id: UUID,
    intent_id: UUID,
    intent_request_name: str,
    intent_original_query: str,
):
    try:
        intent_text = f"""
        {intent_request_name} {intent_original_query}
        """
        provider = LLMProviderFactory.create(settings.llm_provider)
        embeddings = provider.get_embedding(intent_text)
        intent_service = get_intent_service_for_celery()
        intent_service.store_intent_embedding(
            tenant_id=tenant_id, intent_id=intent_id, intent_embedding=embeddings
        )
        logger.info("Intent embeddings added for the intent")
    except Exception as exc:
        logger.error(
            f"Task failed for getting embedding for the intent id={intent_id}: {exc}"
        )
        raise self.retry(exc=exc)


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
        discover_search_urls.delay(job_run_id)
        return {"job_run_id": job_run_id, "queries_generated": len(created)}
    except Exception as exc:
        # The service has already marked the run FAILED; retry transient errors.
        logger.error(f"Task failed for job_run={job_run_id}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(
    name="search_worker.discover_search_urls",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    acks_late=True,
)
def discover_search_urls(self, job_run_id: str):
    logger.info(f"REceived URL Discovery task for job run={job_run_id}")
    service = build_search_url_service()
    try:
        count = service.discover_for_job_run(job_run_id=UUID(job_run_id))
        logger.info(f"Discovered {count} URLS for job_run={job_run_id}")
        return {"job_run_id": job_run_id, "urls_discovered": count}
    except Exception as exc:
        logger.error(f"URL Discovery task failed for job_run={job_run_id}: {exc}")
        raise self.retry(exc=exc)
