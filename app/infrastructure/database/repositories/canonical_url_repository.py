from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.infrastructure.database.models.canonical_url import CanonicalUrl
from app.core.schemas.search_url_schemas import CanonicalUrlCreate


class CanonicalUrlRepo:
    def __init__(self, db):
        self.db = db

    def get_or_create_many(
        self, items: list[CanonicalUrlCreate]
    ) -> dict[str, CanonicalUrl]:
        if not items:
            return {}
        rows = [
            {
                "normalized_url": i.normalized_url,
                "url": i.url,
                "domain": i.domain,
                "title": i.title,
            }
            for i in items
        ]
        stmt = (
            pg_insert(CanonicalUrl)
            .values(rows)
            .on_conflict_do_nothing(index_elements=["normalized_url"])
        )
        self.db.execute(stmt)
        self.db.flush()

        keys = [i.normalized_url for i in items]
        existing = (
            self.db.query(CanonicalUrl)
            .filter(CanonicalUrl.normalized_url.in_(keys))
            .all()
        )
        return {c.normalized_url: c for c in existing}
