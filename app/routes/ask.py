from fastapi import APIRouter, HTTPException, Depends
from app.models.models import AskRequest, AskResponse
from app.services.rag_pipeline import run_faq_pipeline
from app.utils.rate_limit import check_rate_limit

router = APIRouter()

@router.post("/ask", response_model=AskResponse, dependencies=[Depends(check_rate_limit)])
async def ask_question(request: AskRequest):
    """Answers a mental health query using RAG with rate limiting and semantic caching."""
    try:
        result = await run_faq_pipeline(request.query)
        return result
    except Exception as e:
        # Proper error logging in a real app
        raise HTTPException(status_code=500, detail=str(e))
