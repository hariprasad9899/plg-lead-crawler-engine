from enum import Enum

from sqlalchemy import Enum as SqlEnum


class CrawlStatusEnum(str, Enum):
    """Shared crawl lifecycle status.

    Used by both ``canonical_urls`` (global crawl state) and
    ``discovered_urls`` (per-tenant discovery state). Both map to the same
    PostgreSQL enum type ``crawl_status``, so the definition must live in a
    single place to avoid emitting ``CREATE TYPE crawl_status`` twice.
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Single shared type instance reused by every column that stores a crawl
# status. Sharing one object (rather than constructing ``SqlEnum`` inline in
# each model) ensures the ``crawl_status`` Postgres type is created exactly
# once.
crawl_status_type = SqlEnum(
    CrawlStatusEnum,
    name="crawl_status",
    values_callable=lambda obj: [e.value for e in obj],
)
