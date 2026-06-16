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

    # search url generation
    search_provider: str = "serper"
    serper_api_key: str = ""
    serper_base_url: str = "https://google.serper.dev/search"
    serper_num_results: int = 10
    serper_timeout: float = 30.0
    serper_max_retries: int = 2

    class Config:
        env_file = ".env"


settings = Settings()
