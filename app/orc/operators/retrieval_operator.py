# app/orc/operators/retrieval_operator.py

import time
from typing import List
from sqlalchemy.orm import Session

from app.models.chunk import ChunkORM
from app.rag.retriever import retrieve_relevant_chunks


class RetrievalOperator:
    """
    Retrieves top-k pgvector chunks relevant to the question.
    """

    def __init__(self, embedder, db: Session, k: int = 10):
        self.embedder = embedder
        self.db = db
        self.k = k

    def __call__(self, question: str, allowed_tags: list[str]) -> List[ChunkORM]:
        return retrieve_relevant_chunks(
            question=question,
            embedder=self.embedder,
            db=self.db,
            allowed_product_tags=allowed_tags,
            k=self.k,
        )
