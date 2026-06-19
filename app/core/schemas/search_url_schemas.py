from pydantic import BaseModel, Field, ConfigDict
from dataclasses import dataclass
from uuid import UUID


class SerpOrganicResult(BaseModel):
    title: str | None = None
    link: str
    snippet: str | None = None
    position: int | None = None


class SerpResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    query: str
    organic: list[SerpOrganicResult] = Field(default_factory=list)


@dataclass
class CanonicalUrlCreate:
    normalized_url: str
    url: str
    domain: str
    title: str | None = None


@dataclass
class DiscoveredUrlCreate:
    tenant_id: UUID
    canonical_url_id: UUID
    search_query_id: UUID
    source_engine: str
    priority_score: int = 50
    discovery_depth: int = 0
