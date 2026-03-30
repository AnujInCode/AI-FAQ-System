import asyncio
from app.config.config import get_settings

settings = get_settings()

async def generate_answer(query: str, context: str) -> str:
    """Mock implementation for local demo: Extracts answer from context to simulate LLM."""
    
    # Simulate API latency
    await asyncio.sleep(0.8)

    # In a real implementation with Anthropic:
    # return anthropic.Anthropic().messages.create(...)

    # If the user asks a dangerous question, simulate fallback
    lower_query = query.lower()
    dangerous_keywords = ['medication', 'prescribe', 'kill', 'suicide', 'drugs']
    if any(keyword in lower_query for keyword in dangerous_keywords):
        return settings.FALLBACK_RESPONSE

    if not context or "A:" not in context:
        return settings.FALLBACK_RESPONSE

    # Naive extraction for the fake LLM mode:
    # Just grab the first answer block cleanly
    try:
        parts = context.split("A:")
        if len(parts) > 1:
            answer = parts[1].split("Q:")[0].strip()
            return f"{answer}"
        return settings.FALLBACK_RESPONSE
    except Exception:
        return settings.FALLBACK_RESPONSE
