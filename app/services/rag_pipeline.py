import time
from app.services.embedding_service import get_embedding
from app.services.retrieval_service import search_faqs
from app.services.llm_service import generate_answer
from app.db.supabase_client import supabase
from app.config.config import get_settings
from app.utils.cache import rag_cache

settings = get_settings()

async def run_faq_pipeline(query: str):
    """Orchestrates the RAG flow: Embed -> Retrieve -> Rank -> Generate -> Log."""
    start_time = time.time()

    # 0. Handle simple greetings instantly
    if query.strip().lower() in ["hi", "hello", "hey", "greetings"]:
        return {
            "answer": "Hello! How can I help you with finding a therapist or understanding our mental health services today?",
            "confidence": 1.0,
            "sources": [],
            "matched_faq_ids": [],
            "latency_ms": int((time.time() - start_time) * 1000)
        }

    # 1. Caching Layer (High Impact for <3s requirement)
    if query in rag_cache:
        # Cache hit - return fast!
        cached_result = rag_cache[query].copy()
        # Still update latency for cache analytics tracking
        cached_result["latency_ms"] = int((time.time() - start_time) * 1000)
        cached_result["cached"] = True 
        return cached_result

    # 2. Generate query embedding
    query_embedding = await get_embedding(query)

    # 3. Perform vector search
    matches = await search_faqs(query_embedding)

    # 4. Re-rank results (Optional Senior step to guarantee best order)
    # Using similarity score for simple re-ranking; can be upgraded to LLM re-ranker
    if matches:
        matches = sorted(matches, key=lambda x: x["similarity"], reverse=True)

    # 5. Process matches
    if not matches:
        # Log unanswered query
        await supabase.table("unanswered_queries").insert({"query": query}).execute()
        return {
            "answer": settings.FALLBACK_RESPONSE,
            "confidence": 0.0,
            "sources": [],
            "matched_faq_ids": [],
            "latency_ms": int((time.time() - start_time) * 1000)
        }

    # Primary confidence metric is highest similarity match
    confidence = matches[0]["similarity"]
    
    # Store analytics arrays
    matched_faq_ids = [m["id"] for m in matches]
    top_scores = [m["similarity"] for m in matches]
    sources = [m["question"] for m in matches]

    # 6. Build context
    context = "\n\n".join([f"Q: {m['question']}\nA: {m['answer']}" for m in matches])

    # 7. Generate grounded answer
    answer = await generate_answer(query, context)
    
    # 8. Domain-Aware Fallback (Check if LLM confirms no answer)
    if "I'm not sure" in answer or settings.FALLBACK_RESPONSE in answer:
        # Log as unanswered for manual review
        await supabase.table("unanswered_queries").insert({"query": query}).execute()
        confidence = 0.0 # Adjust confidence for fallback
        answer = settings.FALLBACK_RESPONSE

    latency_ms = int((time.time() - start_time) * 1000)

    # 9. Log advanced analytics to DB
    try:
        await supabase.table("query_logs").insert({
            "query": query,
            "response": answer,
            "confidence_score": confidence,
            "sources": sources,
            "matched_faq_ids": matched_faq_ids,
            "top_scores": top_scores,
            "prompt_version": settings.PROMPT_VERSION,
            "latency_ms": latency_ms
        }).execute()
    except Exception as e:
        print(f"Non-critical DB Logging Error: {e}")

    # 10. Prepare result and add to cache
    result = {
        "answer": answer,
        "confidence": round(confidence, 2),
        "sources": sources,
        "matched_faq_ids": matched_faq_ids,
        "latency_ms": latency_ms
    }
    
    # Cache result for 1 hour
    rag_cache[query] = result

    return result