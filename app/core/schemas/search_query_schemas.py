from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SearchStrategy(str, Enum):
    """Generation strategy a query was derived from."""

    INDUSTRY = "industry"
    PERSONA = "persona"
    GEOGRAPHY = "geography"
    HIRING_SIGNAL = "hiring_signal"
    GROWTH_SIGNAL = "growth_signal"
    COMPANY_SIZE = "company_size"
    ALT_TERMINOLOGY = "alt_terminology"
    PROCUREMENT = "procurement"


class GeneratedSearchQuery(BaseModel):
    """A single search query produced by the LLM (structured-output unit)."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=300,
        description="A concrete, ready-to-use search query string for lead discovery.",
    )
    priority: int = Field(
        ...,
        ge=1,
        le=20,
        description="Relative importance, 1 = highest priority.",
    )
    strategy: SearchStrategy = Field(
        ...,
        description="The generation strategy this query belongs to.",
    )

    @field_validator("query")
    @classmethod
    def _strip_query(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("query must not be blank")
        return cleaned


class SearchQueryGenerationResult(BaseModel):
    """Top-level structured-output container returned by the LLM."""

    queries: list[GeneratedSearchQuery] = Field(
        ...,
        min_length=1,
        description="The full set of generated search queries.",
    )


@dataclass
class SearchQueryCreate:
    """Persistence DTO mapped onto the ``search_queries`` table."""

    tenant_id: UUID
    job_run_id: UUID
    query: str
    priority: int
    strategy: str
    llm_provider: str
    llm_model: str
