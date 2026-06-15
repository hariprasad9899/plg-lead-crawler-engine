from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str

    # LLM / search-query generation
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.7
    llm_max_retries: int = 2
    openai_api_key: str = ""
    search_query_min: int = 1
    search_query_max: int = 1

    class Config:
        env_file = ".env"


settings = Settings()
