from functools import lru_cache
from typing import List

from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def load_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> List[float]:
    model = load_embedding_model()
    embedding = model.encode(text)
    return embedding.tolist()


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    model = load_embedding_model()
    embeddings = model.encode(texts)
    return [embedding.tolist() for embedding in embeddings]