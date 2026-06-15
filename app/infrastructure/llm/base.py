from abc import ABC, abstractmethod

from langchain_core.runnables import Runnable
from pydantic import BaseModel


class BaseLLMProvider(ABC):
    """
    Provider-agnostic abstraction over a chat LLM.

    Concrete providers wrap a specific vendor SDK (OpenAI, etc.) and expose a
    single capability used by this module: producing a runnable that returns a
    validated Pydantic object via the vendor's structured-output mechanism.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Short provider identifier persisted alongside generated queries."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """The concrete model identifier (e.g. ``gpt-4o-mini``)."""
        ...

    @abstractmethod
    def get_structured_llm(self, schema: type[BaseModel]) -> Runnable:
        """
        Return a runnable that, when invoked with a list of chat messages,
        produces an instance of ``schema`` validated by the vendor.
        """
        ...
