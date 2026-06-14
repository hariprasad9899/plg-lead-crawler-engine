from app.core.queue.celery_app import celery_app
from app.core.logger.logger import get_logger

logger = get_logger()


@celery_app.task
def generate_search_queries(job_run_id: str):
    logger.info(f"Received Message through Queue {job_run_id}")
    print(job_run_id)
