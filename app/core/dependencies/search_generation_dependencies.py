from app.core.ai.search_query.intent_generator import IntentGenerator
from app.core.ai.search_query.prompt_builder import PromptBuilder
from app.core.services.search_generation_service import SearchGenerationService
from app.core.utils.env_config import settings
from app.infrastructure.database.sessions.session import SessionLocal
from app.infrastructure.llm.provider_factory import LLMProviderFactory


def build_search_generation_service() -> SearchGenerationService:
    """
    Assemble the search-generation object graph for the Celery worker.

    Mirrors the FastAPI dependency builders but takes no request scope — the
    service opens its own DB session per task via ``SessionLocal``.
    """
    provider = LLMProviderFactory.create(settings.llm_provider)
    prompt_builder = PromptBuilder(
        min_queries=settings.search_query_min,
        max_queries=settings.search_query_max,
    )
    generator = IntentGenerator(
        provider=provider,
        prompt_builder=prompt_builder,
        max_queries=settings.search_query_max,
    )
    return SearchGenerationService(
        session_factory=SessionLocal,
        generator=generator,
    )
