from app.infrastructure.search.base import BaseSearchProvider
from app.core.schemas.search_url_schemas import SerpResult
import httpx


class SerperProvider(BaseSearchProvider):

    PROVIDER_NAME = "serper"

    def __init__(
        self,
        api_key: str,
        base_url: str,
        num_results: int,
        timeout: int,
        max_retries: int,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.num_results = num_results
        self.timeout = timeout
        self.max_retries = max_retries

    @property
    def provider_name(self):
        return self.PROVIDER_NAME

    def search(self, query: str) -> SerpResult:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                self.base_url,
                headers={"X-API-KEY": self.api_key},
                json={"q": query, "num": self.num_results},
            )
            response.raise_for_status()
            data = response.json()
        return SerpResult(query=query, organic=data.get("organic", []))
