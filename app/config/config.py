from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str  # Service role key recommended for backend ops

    # OpenAI
    OPENAI_API_KEY: str
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Anthropic
    ANTHROPIC_API_KEY: str
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20240620"

    # RAG Settings
    RAG_THRESHOLD: float = 0.3
    TOP_K: int = 3
    FALLBACK_RESPONSE: str = "I'm not fully sure about this, but I can help you connect with a licensed therapist immediately."

    # App
    PROJECT_NAME: str = "Psychology FAQ System"
    VERSION: str = "0.1.0"

    # Prompt Version Tracking for logging
    PROMPT_VERSION: str = "v1.1-safe-fallback"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache()
def get_settings():
    return Settings()
