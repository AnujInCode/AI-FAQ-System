from app.config.config import get_settings
import numpy as np

settings = get_settings()

# Initialize the model only if needed (singleton pattern)
_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading local sentence-transformers model...")
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model

async def get_embedding(text: str) -> list[float]:
    """Generates an embedding for the given text using a local HuggingFace model."""
    model = get_model()
    # model.encode returns a numpy array, we need a list of floats
    embedding = model.encode(text)
    return embedding.tolist()
