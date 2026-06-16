from sqlalchemy.dialects.postgresql import insert as pg_insert
from dataclasses import asdict
from app.core.schemas.search_url_schemas import DiscoveredUrlCreate
from app.infrastructure.database.models.discovered_url import DiscoveredUrl


class DiscoveredUrlRepo:

    def __init__(self, db):
        self.db = db

    def bulk_create(self, items: list[DiscoveredUrlCreate]) -> int:
        if not items:
            return 0
        stmt = (
            pg_insert(DiscoveredUrl)
            .values([asdict(i) for i in items])
            .on_conflict_do_nothing(constraint="uq_discovered_tenant_canonical_query")
        )
        result = self.db.execute(stmt)
        self.db.flush()
        return result.rowcount
