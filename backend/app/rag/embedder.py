# app/rag/embedder.py

from typing import List, Sequence
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config.settings import get_settings

settings = get_settings()


class Embedder:
    """
    Wrapper around a sentence-transformers embedding model.
    """

    def __init__(self, model_name: str | None = None):
        if model_name is None:
            model_name = settings.embedding_model_name

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        """
        Compute embeddings for a list of texts.
        Returns a list of float vectors.
        """
        if not texts:
            return []

        # sentence-transformers returns numpy arrays; convert to Python lists
        embeddings = self.model.encode(
            list(texts),
            batch_size=settings.embedding_batch_size,
            show_progress_bar=False,
        )
        return [emb.tolist() for emb in embeddings]


@lru_cache()
def get_embedder() -> Embedder:
    """
    Cached global Embedder instance.
    """
    return Embedder()
