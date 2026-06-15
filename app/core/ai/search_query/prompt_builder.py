import json

from langchain_core.messages import BaseMessage

from app.core.ai.search_query.prompts import (
    STRATEGY_GUIDE,
    build_chat_prompt,
)
from app.core.schemas.intents_schemas import IntentGenerationInput


class PromptBuilder:
    """
    Turns an :class:`IntentGenerationInput` into a list of chat messages.

    Holds no LLM dependency — it only formats runtime context onto the static
    templates declared in ``prompts.py``.
    """

    def __init__(self, min_queries: int, max_queries: int):
        self._min_queries = min_queries
        self._max_queries = max_queries
        self._template = build_chat_prompt()

    def build(self, intent_input: IntentGenerationInput) -> list[BaseMessage]:
        config = intent_input.config or {}
        config_json = json.dumps(config, indent=2, ensure_ascii=False)

        return self._template.format_messages(
            min_queries=self._min_queries,
            max_queries=self._max_queries,
            strategy_guide=STRATEGY_GUIDE,
            request_name=intent_input.request_name,
            original_query=intent_input.original_query,
            config_name=intent_input.config_name,
            config_description=intent_input.config_description
            or "No description provided.",
            config_json=config_json,
        )
