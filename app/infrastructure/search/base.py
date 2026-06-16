from abc import ABC, abstractmethod
from langchain_core.runnables import Runnable
from pydantic import BaseModel
from app.core.schemas.search_url_schemas import SerpResult


class BaseSearchProvider(ABC):

    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @abstractmethod
    def search(self, query: str) -> SerpResult: ...
