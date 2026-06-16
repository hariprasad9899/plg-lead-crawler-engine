from typing import Callable
from uuid import UUID
from sqlalchemy.orm import Session as SQLAlchemySession
from app.core.exceptions.base import AppException
from app.core.exceptions.error_catalog import JOB_RUN_NOT_FOUND
from app.core.logger import get_logger
from app.infrastructure.database.repositories.job_run_repository import JobRunRepo
from app.infrastructure.database.repositories.search_query_repository import (
    SearchQueryRepo,
    QueryStatusEnum,
)
from app.infrastructure.database.repositories.canonical_url_repository import (
    CanonicalUrlRepo,
)
from app.infrastructure.database.repositories.discovered_url_repository import (
    DiscoveredUrlRepo,
)
from app.infrastructure.search.base import BaseSearchProvider
from app.core.schemas.search_url_schemas import CanonicalUrlCreate, DiscoveredUrlCreate
from app.core.utils.url_normalize import normalize_url
from app.infrastructure.database.models.search_query import SearchQuery

logger = get_logger(__name__)


class SearchUrlService:

    def __init__(
        self,
        session_factory: Callable[[], SQLAlchemySession],
        provider: BaseSearchProvider,
    ):
        self._session_factory = session_factory
        self._provider = provider

    def discover_for_job_run(
        self,
        job_run_id: UUID,
    ) -> int:
        db = self._session_factory()
        try:
            job_run_repo = JobRunRepo(db=db)
            search_query_repo = SearchQueryRepo(db=db)
            canonical_repo = CanonicalUrlRepo(db=db)
            discovered_repo = DiscoveredUrlRepo(db=db)

            job_run = job_run_repo.get_by_id(job_run_id=job_run_id)
            if not job_run:
                raise AppException(JOB_RUN_NOT_FOUND)
            tenant_id = job_run.tenant_id

            queries = search_query_repo.list_pending_for_job_run(
                job_run_id=job_run_id, tenant_id=tenant_id
            )
            if not queries:
                logger.info(f"No pending queries for job_run={job_run_id}")
                return 0
            total_new = 0
            for q in queries:
                try:
                    total_new += self._process_query(
                        q, tenant_id, canonical_repo, discovered_repo
                    )
                    search_query_repo.mark_status(q, QueryStatusEnum.COMPLETED)
                    db.commit()
                except Exception as exc:
                    db.rollback()
                    logger.error(f"Query {q.id} failed: {exc}")
                    search_query_repo.mark_status(q, QueryStatusEnum.FAILED)
                    db.commit()
            return total_new
        except Exception as exc:
            db.rollback()
            logger.error(f"URL discovery failed for job_run={job_run_id}: {exc}")
            raise
        finally:
            db.close()

    def _process_query(
        self,
        q: SearchQuery,
        tenant_id: UUID,
        canonical_repo: CanonicalUrlRepo,
        discovered_repo: DiscoveredUrlRepo,
    ) -> int:
        result = self._provider.search(q.query)

        # 1. Normalize + filter junk, dedupe within this query
        seen: dict[str, CanonicalUrlCreate] = {}
        scores: dict[str, int] = {}
        for idx, item in enumerate(result.organic, start=1):
            if not item.link:
                continue
            normalized, domain = normalize_url(item.link)
            if not domain:
                continue
            position = item.position or idx
            if normalized not in seen:
                seen[normalized] = CanonicalUrlCreate(
                    normalized_url=normalized,
                    url=item.link,
                    domain=domain,
                    title=item.title,
                )
                scores[normalized] = self._score(q.priority, position)

        if not seen:
            return 0

        # 2. get-or-create canonicals -> {normalized_url: CanonicalUrl}
        canonical_map = canonical_repo.get_or_create_many(list(seen.values()))

        # 3. build DiscoveredUrlCreate rows
        discovered = [
            DiscoveredUrlCreate(
                tenant_id=tenant_id,
                canonical_url_id=canonical_map[norm].id,
                search_query_id=q.id,
                source_engine=self._provider.provider_name,
                priority_score=scores[norm],
            )
            for norm in seen
        ]
        return discovered_repo.bulk_create(discovered)

    @staticmethod
    def _score(query_priority: int, position: int) -> int:
        return max(1, min(100, (21 - query_priority) * 5 - position))
