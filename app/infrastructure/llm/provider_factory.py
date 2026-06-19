from app.core.exceptions.base import AppException
from app.core.exceptions.error_catalog import LLM_PROVIDER_NOT_CONFIGURED
from app.core.utils.env_config import settings
from app.infrastructure.llm.base import BaseLLMProvider
from app.infrastructure.llm.openai_provider import OpenAIProvider


class LLMProviderFactory:
    """Resolves a configured :class:`BaseLLMProvider` by name."""

    @staticmethod
    def create(provider_name: str | None = None) -> BaseLLMProvider:
        provider = (provider_name or settings.llm_provider).lower()

        if provider == OpenAIProvider.PROVIDER_NAME:
            if not settings.openai_api_key:
                raise AppException(
                    LLM_PROVIDER_NOT_CONFIGURED,
                    details="OPENAI_API_KEY is not set.",
                )
            return OpenAIProvider(
                api_key=settings.openai_api_key,
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                max_retries=settings.llm_max_retries,
            )

        raise AppException(
            LLM_PROVIDER_NOT_CONFIGURED,
            details=f"Unsupported LLM provider: {provider}",
        )
