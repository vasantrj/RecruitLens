from functools import lru_cache
from sentence_transformers import SentenceTransformer, util

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model():
    return SentenceTransformer(MODEL_NAME)


def embed_text(text: str):
    model = get_embedding_model()
    return model.encode(text, convert_to_tensor=True)


def cosine_similarity(text_a: str, text_b: str) -> float:
    if not text_a or not text_b:
        return 0.0
    model = get_embedding_model()
    embeddings = model.encode([text_a, text_b], convert_to_tensor=True)
    score = util.cos_sim(embeddings[0], embeddings[1]).item()
    return max(0.0, min(1.0, score))