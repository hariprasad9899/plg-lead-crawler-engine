from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.infrastructure.llm.base import BaseLLMProvider
from app.core.logger import get_logger

logger = get_logger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI-backed provider built on ``langchain_openai.ChatOpenAI``."""

    PROVIDER_NAME = "openai"

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float = 0.7,
        max_retries: int = 2,
        timeout: float = 60.0,
    ):
        self._model = model
        self._llm = ChatOpenAI(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_retries=max_retries,
            timeout=timeout,
        )
        logger.info(f"Initialized OpenAIProvider with model={model}")

    @property
    def provider_name(self) -> str:
        return self.PROVIDER_NAME

    @property
    def model_name(self) -> str:
        return self._model

    def get_structured_llm(self, schema: type[BaseModel]) -> Runnable:
        # function_calling is the most reliable structured-output path for
        # OpenAI chat models and guarantees a validated Pydantic instance.
        return self._llm.with_structured_output(schema, method="function_calling")
