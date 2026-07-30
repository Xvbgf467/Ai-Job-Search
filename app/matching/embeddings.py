from functools import lru_cache

import numpy as np

from app.config import settings


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.embedding_model)


def embed(text: str) -> np.ndarray:
    return _model().encode(text, normalize_embeddings=True)


def embed_batch(texts: list[str]) -> np.ndarray:
    return _model().encode(texts, normalize_embeddings=True)


def similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))
