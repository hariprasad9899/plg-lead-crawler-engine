from typing import Callable
from uuid import UUID

from sqlalchemy.orm import Session as SQLAlchemySession

from app.core.ai.search_query.intent_generator import IntentGenerator
from app.core.exceptions.base import AppException
from app.core.exceptions.error_catalog import JOB_RUN_NOT_FOUND
from app.core.logger import get_logger
from app.core.schemas.intents_schemas import IntentGenerationInput
from app.core.schemas.search_query_schemas import SearchQueryCreate
from app.infrastructure.database.models.search_query import SearchQuery
from app.infrastructure.database.repositories.job_run_repository import JobRunRepo
from app.infrastructure.database.repositories.search_query_repository import (
    SearchQueryRepo,
)

logger = get_logger(__name__)


class SearchGenerationService:
    """
    Generates and persists search queries for a single ``JobRun``.

    Runs inside a Celery worker, so it owns its unit of work: it opens a session
    per call, drives status transitions on the job run, and isolates the
    failure path in a fresh session so the run is always marked FAILED.
    """

    def __init__(
        self,
        session_factory: Callable[[], SQLAlchemySession],
        generator: IntentGenerator,
    ):
        self._session_factory = session_factory
        self._generator = generator

    def generate_for_job_run(
        self, job_run_id: UUID, intent_input: IntentGenerationInput
    ) -> list[SearchQuery]:
        db = self._session_factory()
        try:
            job_run_repo = JobRunRepo(db=db)
            search_query_repo = SearchQueryRepo(db=db)

            job_run = job_run_repo.get_by_id(job_run_id=job_run_id)
            if not job_run:
                raise AppException(JOB_RUN_NOT_FOUND)

            tenant_id = job_run.tenant_id
            job_run_repo.mark_running(job_run)
            db.commit()

            generated = self._generator.generate(intent_input)

            items = [
                SearchQueryCreate(
                    tenant_id=tenant_id,
                    job_run_id=job_run_id,
                    query=q.query,
                    priority=q.priority,
                    strategy=q.strategy.value,
                    llm_provider=self._generator.provider.provider_name,
                    llm_model=self._generator.provider.model_name,
                )
                for q in generated
            ]
            created = search_query_repo.bulk_create(items)

            job_run_repo.mark_completed(job_run, seed_urls_count=len(created))
            db.commit()

            logger.info(
                f"Persisted {len(created)} search queries for job_run={job_run_id}"
            )
            return created
        except Exception as exc:
            db.rollback()
            logger.error(f"Search generation failed for job_run={job_run_id}: {exc}")
            self._mark_failed(job_run_id)
            raise
        finally:
            db.close()

    def _mark_failed(self, job_run_id: UUID) -> None:
        """Mark the run FAILED in an isolated session, swallowing errors."""
        db = self._session_factory()
        try:
            job_run_repo = JobRunRepo(db=db)
            job_run = job_run_repo.get_by_id(job_run_id=job_run_id)
            if job_run:
                job_run_repo.mark_failed(job_run)
                db.commit()
        except Exception as exc:
            db.rollback()
            logger.error(f"Could not mark job_run={job_run_id} FAILED: {exc}")
        finally:
            db.close()
