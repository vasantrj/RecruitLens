from functools import lru_cache
from sentence_transformers import CrossEncoder

RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


@lru_cache(maxsize=1)
def get_reranker_model():
    return CrossEncoder(RERANKER_MODEL_NAME)


def rerank_score(jd_text: str, resume_text: str) -> float:
    """
    Returns a relevance score (raw logit, roughly -10 to 10) for how well
    the resume matches the JD, evaluated jointly rather than independently.
    Normalized to a 0-1 range using a sigmoid.
    """
    import math

    model = get_reranker_model()
    raw_score = model.predict([(jd_text, resume_text)])[0]
    normalized = 1 / (1 + math.exp(-raw_score))
    return float(normalized)