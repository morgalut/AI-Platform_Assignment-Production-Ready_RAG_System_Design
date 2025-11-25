# app/rag/retriever.py

from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chunk import ChunkORM
from app.models.query import UsedChunk


def retrieve_relevant_chunks(
    question: str,
    embedder,
    db: Session,
    allowed_product_tags: List[str],
    k: int = 10,
):
    """
    Retrieve top-k relevant chunks using pgvector L2 distance.
    """

    # Embed question → embedder expects a list
    vectors = embedder.embed([question])

    if not vectors or not isinstance(vectors[0], list):
        raise ValueError(f"Invalid embedding returned from embedder: {vectors}")

    embedding_vector = vectors[0]

    stmt = (
        select(ChunkORM)
        .where(ChunkORM.product_tag.in_(allowed_product_tags))
        .order_by(ChunkORM.embedding.l2_distance(embedding_vector))
        .limit(k)
    )

    return db.execute(stmt).scalars().all()


def chunks_to_used_chunks(chunks: list[ChunkORM]) -> list[UsedChunk]:
    """
    Convert SQLAlchemy ChunkORM → Pydantic UsedChunk (safe for API response).
    """
    return [
        UsedChunk(
            ticket_id=c.ticket_id,
            product_tag=c.product_tag,
            chunk_index=c.chunk_index,
            text=c.text,
        )
        for c in chunks
    ]
