from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Environment
    environment: str = "development"
    log_level: str = "INFO"

    # Weaviate
    weaviate_url: str = "http://localhost:8080"
    weaviate_collection: str = "hipaa"

    # Gemini
    gemini_api_key: str = "AIzaSyCa28bViRyRqQlDEaxtlzciFRFkghyb9hk"
    gemini_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "text-embedding-004"

    # Embedding config
    embedding_dimensions: int = 768

    # RAG config
    retrieval_top_k: int = 3

    # Slack
    slack_bot_token: str = ""
    slack_signing_secret: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
