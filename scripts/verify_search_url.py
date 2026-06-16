"""
Manual end-to-end check for the URL-discovery stage — no Celery/Redis needed.

Runs SearchUrlService.discover_for_job_run() directly against a real job run,
then prints how many canonical_urls / discovered_urls landed for it.

Usage:
    python -m scripts.verify_search_url <job_run_id>

Prereqs: that job run must already have PENDING rows in search_queries
(i.e. the generate_search_queries stage ran first), and SERPER_API_KEY must
be set in .env.
"""

import sys
from uuid import UUID

from app.core.dependencies.search_url_dependencies import build_search_url_service
from app.infrastructure.database.models.canonical_url import CanonicalUrl
from app.infrastructure.database.models.discovered_url import DiscoveredUrl
from app.infrastructure.database.sessions.session import SessionLocal


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: python -m scripts.verify_search_url <job_run_id>")
        raise SystemExit(2)

    job_run_id = UUID(sys.argv[1])

    service = build_search_url_service()
    count = service.discover_for_job_run(job_run_id=job_run_id)
    print(f"\ndiscover_for_job_run returned: {count} new discovered URLs\n")

    # Inspect what actually landed for this job run.
    db = SessionLocal()
    try:
        discovered = (
            db.query(DiscoveredUrl, CanonicalUrl)
            .join(CanonicalUrl, DiscoveredUrl.canonical_url_id == CanonicalUrl.id)
            # scope to this job run via the search_query FK
            .filter(DiscoveredUrl.search_query.has(job_run_id=job_run_id))
            .order_by(DiscoveredUrl.priority_score.desc())
            .all()
        )
        print(f"discovered_urls for job_run={job_run_id}: {len(discovered)} rows")
        for d, c in discovered[:20]:
            print(f"  [{d.priority_score:>3}] {c.domain:<30} {c.normalized_url}")
        if len(discovered) > 20:
            print(f"  ... and {len(discovered) - 20} more")
    finally:
        db.close()


if __name__ == "__main__":
    main()
