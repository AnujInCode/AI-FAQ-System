from postgrest import AsyncPostgrestClient
from app.config.config import get_settings

settings = get_settings()

def get_supabase() -> AsyncPostgrestClient:
    """Returns a direct Async PostgREST client for a generic Postgres docker setup."""
    return AsyncPostgrestClient(settings.SUPABASE_URL)

supabase = get_supabase()
