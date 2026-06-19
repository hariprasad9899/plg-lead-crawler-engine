from app.core.exceptions.base import AppException
from app.core.exceptions.error_catalog import SEARCH_PROVIDER_NOT_CONFIGURED
from app.core.utils.env_config import settings
from app.infrastructure.search.base import BaseSearchProvider
from app.infrastructure.search.serper_provider import SerperProvider


class SearchProviderFactory:

    @staticmethod
    def create(provider_name: str | None = None) -> BaseSearchProvider:
        provider = (provider_name or settings.search_provider).lower()

        if provider == SerperProvider.PROVIDER_NAME:
            if not settings.serper_api_key:
                raise AppException(
                    SEARCH_PROVIDER_NOT_CONFIGURED,
                    details="Search provider key is not set",
                )
            return SerperProvider(
                api_key=settings.serper_api_key,
                base_url=settings.serper_base_url,
                num_results=settings.serper_num_results,
                timeout=settings.serper_timeout,
                max_retries=settings.serper_max_retries,
            )
        raise AppException(
            SEARCH_PROVIDER_NOT_CONFIGURED,
            details=f"Unsupported search provider: {provider}",
        )
