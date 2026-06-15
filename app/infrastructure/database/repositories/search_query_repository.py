from dataclasses import asdict

from sqlalchemy.orm import Session as SQLAlchemySession

from app.core.schemas.search_query_schemas import SearchQueryCreate
from app.infrastructure.database.models.search_query import SearchQuery


class SearchQueryRepo:
    def __init__(self, db: SQLAlchemySession):
        self.db = db

    def bulk_create(self, items: list[SearchQueryCreate]) -> list[SearchQuery]:
        objs = [SearchQuery(**asdict(item)) for item in items]
        self.db.add_all(objs)
        self.db.flush()
        return objs
