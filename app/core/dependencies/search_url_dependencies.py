from app.core.services.search_url_service import SearchUrlService
from app.core.utils.env_config import settings
from app.infrastructure.database.sessions.session import SessionLocal
from app.infrastructure.search.provider_factory import SearchProviderFactory


def build_search_url_service() -> SearchUrlService:
    provider = SearchProviderFactory.create(settings.search_provider)
    return SearchUrlService(session_factory=SessionLocal, provider=provider)
