from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://fmi:fmi_dev_password_change_me@localhost:5432/fmi"
    redis_url: str = "redis://localhost:6379/0"
    api_cors_origins: str = "http://localhost:3000"
    api_key: str = ""
    classification_mode: str = "hybrid"  # rules | llm | hybrid
    llm_provider: str = "none"  # none | ollama | vllm
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    vllm_base_url: str = "http://localhost:8001/v1"
    vllm_api_key: str = ""
    vllm_model: str = ""
    fx_hours_per_day: float = 8.0
    log_level: str = "INFO"
    methodology_version: str = "1.0.0"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.api_cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
