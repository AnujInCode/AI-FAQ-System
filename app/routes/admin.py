from fastapi import APIRouter, HTTPException
from typing import List
from app.models.models import FAQCreate, FAQUpdate, FAQResponse, MetricsResponse, EvaluateRequest, EvaluateResponse
from app.db.supabase_client import supabase
from app.services.embedding_service import get_embedding
from app.services.rag_pipeline import run_faq_pipeline
from datetime import datetime
import numpy as np

router = APIRouter(prefix="/admin")

@router.get("/metrics", response_model=MetricsResponse)
async def get_system_metrics():
    """Returns analytics data across system queries, latencies, and fallback performance."""
    try:
        # Get query stats
        query_logs = await supabase.table("query_logs").select("latency_ms, confidence_score").execute()
        unanswered = await supabase.table("unanswered_queries").select("id", count="exact").execute()
        
        logs = query_logs.data
        total_queries = len(logs)
        unanswered_queries = unanswered.count if unanswered.count else 0
        
        avg_lat = sum(log.get("latency_ms", 0) for log in logs) / total_queries if total_queries else 0
        avg_conf = sum(log.get("confidence_score", 0.0) for log in logs) / total_queries if total_queries else 0.0
        
        return {
            "total_queries": total_queries,
            "unanswered_queries": unanswered_queries,
            "avg_latency_ms": round(avg_lat, 2),
            "avg_confidence": round(avg_conf, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_rag_answer(request: EvaluateRequest):
    """Evaluates the generation pipeline against a known expected answer using cosine similarity distance."""
    # 1. Generate new answer
    rag_result = await run_faq_pipeline(request.query)
    generated_answer = rag_result["answer"]
    
    # 2. Get embeddings for generated answer and expected answer to compute semantic match
    gen_emb = await get_embedding(generated_answer)
    exp_emb = await get_embedding(request.expected_answer)
    
    # Calculate Cosine Similarity
    score = np.dot(gen_emb, exp_emb) / (np.linalg.norm(gen_emb) * np.linalg.norm(exp_emb))
    
    return {
        "score": round(float(score), 2),
        "match": score > 0.85, # True if strongly semantically similar
        "generated_answer": generated_answer
    }

@router.post("/faq", response_model=FAQResponse)
async def create_faq(faq: FAQCreate):
    """Adds a new FAQ and generates its embedding."""
    # Generate embedding
    embedding = await get_embedding(faq.question + " " + faq.answer)
    
    data = {
        "question": faq.question,
        "answer": faq.answer,
        "embedding": embedding
    }
    
    response = await supabase.table("faqs").insert(data).execute()
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create FAQ")
    return response.data[0]

@router.get("/faqs", response_model=List[FAQResponse])
async def list_faqs():
    """Lists all FAQs (without embeddings for performance)."""
    response = await supabase.table("faqs").select("id, question, answer, created_at, updated_at").execute()
    return response.data

@router.put("/faq/{id}", response_model=FAQResponse)
async def update_faq(id: int, faq: FAQUpdate):
    """Updates an FAQ and regenerates its embedding."""
    update_data = faq.model_dump(exclude_unset=True)
    
    if "question" in update_data or "answer" in update_data:
        # Get existing to ensure we have both for re-embedding
        existing = await supabase.table("faqs").select("*").eq("id", id).single().execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="FAQ not found")
        
        q = update_data.get("question", existing.data["question"])
        a = update_data.get("answer", existing.data["answer"])
        update_data["embedding"] = await get_embedding(q + " " + a)
        update_data["updated_at"] = datetime.utcnow().isoformat()

    response = await supabase.table("faqs").update(update_data).eq("id", id).execute()
    return response.data[0]

@router.delete("/faq/{id}")
async def delete_faq(id: int):
    """Deletes an FAQ."""
    await supabase.table("faqs").delete().eq("id", id).execute()
    return {"message": "FAQ deleted"}
