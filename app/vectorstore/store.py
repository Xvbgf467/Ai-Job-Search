import numpy as np

"""Thin FAISS wrapper for fast top-k embedding search.

Swappable: in prod use pgvector instead so vectors live next to job rows.
"""


class VectorStore:
    def __init__(self, dim: int):
        import faiss

        self._index = faiss.IndexFlatIP(dim)   # inner product == cosine for normalized vecs
        self._ids: list[int] = []

    def add(self, job_id: int, vector: np.ndarray) -> None:
        self._index.add(np.asarray([vector]).astype("float32"))
        self._ids.append(job_id)

    def search(self, vector: np.ndarray, k: int = 50) -> list[tuple[int, float]]:
        d, i = self._index.search(np.asarray([vector]).astype("float32"), k)
        return [(self._ids[idx], float(score)) for score, idx in zip(d[0], i[0]) if idx >= 0]
