from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "dev"
    database_url: str = "sqlite:///./techmatch.db"

    # Sourcing — public APIs
    adzuna_app_id: str = ""
    adzuna_api_key: str = ""
    usajobs_api_key: str = ""
    remote_api_base: str = "https://remotive.com/api"

    # Sourcing — scrapers
    scrape_enabled: bool = False
    user_agent: str = "TechMatchBot/0.1"
    proxy_url: str = ""

    # Matching
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    llm_provider: str = ""        # zai | openai | anthropic
    llm_model: str = ""           # e.g. glm-4.6
    llm_base_url: str = ""        # zai: https://api.z.ai/api/paas/v4/
    llm_api_key: str = ""         # LLM_API_KEY
    llm_rerank_top_n: int = 20
    llm_timeout: float = 30.0     # hard cap so a stalled provider can't hang the request

    @property
    def llm_enabled(self) -> bool:
        return bool(self.llm_provider and self.llm_model and self.llm_api_key)


settings = Settings()
