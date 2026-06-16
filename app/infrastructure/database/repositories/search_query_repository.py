from dataclasses import asdict
from sqlalchemy.orm import Session as SQLAlchemySession
from app.core.schemas.search_query_schemas import SearchQueryCreate
from app.infrastructure.database.models.search_query import SearchQuery, QueryStatusEnum
from uuid import UUID


class SearchQueryRepo:
    def __init__(self, db: SQLAlchemySession):
        self.db = db

    def bulk_create(self, items: list[SearchQueryCreate]) -> list[SearchQuery]:
        objs = [SearchQuery(**asdict(item)) for item in items]
        self.db.add_all(objs)
        self.db.flush()
        return objs

    def list_pending_for_job_run(
        self, job_run_id: UUID, tenant_id: UUID
    ) -> list[SearchQuery]:
        return (
            self.db.query(SearchQuery)
            .filter(
                SearchQuery.job_run_id == job_run_id,
                SearchQuery.tenant_id == tenant_id,
                SearchQuery.status == QueryStatusEnum.PENDING,
            )
            .order_by(SearchQuery.priority.asc())
            .all()
        )

    def mark_status(self, query: SearchQuery, status: QueryStatusEnum) -> None:
        query.status = status
