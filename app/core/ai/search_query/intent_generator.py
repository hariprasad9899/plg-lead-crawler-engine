from app.core.ai.search_query.prompt_builder import PromptBuilder
from app.core.exceptions.base import AppException
from app.core.exceptions.error_catalog import SEARCH_QUERY_GENERATION_FAILED
from app.core.logger import get_logger
from app.core.schemas.intents_schemas import IntentGenerationInput
from app.core.schemas.search_query_schemas import (
    GeneratedSearchQuery,
    SearchQueryGenerationResult,
)
from app.infrastructure.llm.base import BaseLLMProvider

logger = get_logger(__name__)


class IntentGenerator:
    """
    Drives the LLM to generate search queries from an intent.

    Owns the provider + prompt builder, invokes the structured-output runnable,
    then validates, de-duplicates and bounds the result.
    """

    def __init__(
        self,
        provider: BaseLLMProvider,
        prompt_builder: PromptBuilder,
        max_queries: int,
    ):
        self._provider = provider
        self._prompt_builder = prompt_builder
        self._max_queries = max_queries

    @property
    def provider(self) -> BaseLLMProvider:
        return self._provider

    def generate(
        self, intent_input: IntentGenerationInput
    ) -> list[GeneratedSearchQuery]:
        messages = self._prompt_builder.build(intent_input)
        structured_llm = self._provider.get_structured_llm(SearchQueryGenerationResult)

        try:
            result: SearchQueryGenerationResult = structured_llm.invoke(messages)
        except Exception as exc:
            logger.error(f"LLM query generation failed: {exc}")
            raise AppException(
                SEARCH_QUERY_GENERATION_FAILED, details=str(exc)
            ) from exc

        queries = self._postprocess(result.queries)
        if not queries:
            raise AppException(
                SEARCH_QUERY_GENERATION_FAILED,
                details="LLM returned no usable queries.",
            )

        logger.info(f"Generated {len(queries)} search queries")
        return queries

    def _postprocess(
        self, queries: list[GeneratedSearchQuery]
    ) -> list[GeneratedSearchQuery]:
        seen: set[str] = set()
        deduped: list[GeneratedSearchQuery] = []
        for q in queries:
            key = q.query.casefold()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(q)

        deduped.sort(key=lambda q: q.priority)
        return deduped[: self._max_queries]
