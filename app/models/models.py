from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class FAQBase(BaseModel):
    question: str
    answer: str

class FAQCreate(FAQBase):
    pass

class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None

class FAQResponse(FAQBase):
    id: int
    created_at: datetime
    updated_at: datetime

class AskRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)

class AskResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[str]
    latency_ms: int
    matched_faq_ids: List[int] = [] # Upgraded payload transparency
    
class EvaluateRequest(BaseModel):
    query: str
    expected_answer: str

class EvaluateResponse(BaseModel):
    score: float
    match: bool
    generated_answer: str

class MetricsResponse(BaseModel):
    total_queries: int
    unanswered_queries: int
    avg_latency_ms: float
    avg_confidence: float
