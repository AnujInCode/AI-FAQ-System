from app.db.supabase_client import supabase
from app.config.config import get_settings

settings = get_settings()

async def search_faqs(query_embedding: list[float], threshold: float = None, top_k: int = None):
    """Searches for FAQs similar to the query embedding."""
    threshold = threshold or settings.RAG_THRESHOLD
    top_k = top_k or settings.TOP_K

    # Use the PostgREST RPC to call the database function
    response = await supabase.rpc(
        "match_faqs",
        {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": top_k
        }
    ).execute()

    return response.data
