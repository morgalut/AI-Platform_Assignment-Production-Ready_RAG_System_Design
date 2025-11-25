# app/rag/retriever.py

from sqlalchemy.orm import Session
from app.models.chunk import ChunkORM, Chunk


def retrieve_relevant_chunks(
    question: str,
    embedder,
    db: Session,
    allowed_product_tags: list[str],
    k: int = 10,
):
    # Embed the user question
    query_embedding = embedder.embed(question)

    # pgvector distance search using .l2_distance()
    rows = (
        db.query(ChunkORM)
        .filter(ChunkORM.product_tag.in_(allowed_product_tags))
        .order_by(ChunkORM.embedding.l2_distance(query_embedding))
        .limit(k)
        .all()
    )

    return rows


def chunks_to_used_chunks(chunks: list[ChunkORM]) -> list[Chunk]:
    """
    Convert SQLAlchemy ORM rows → Pydantic models.
    """
    return [
        Chunk.model_validate(chunk, from_attributes=True)
        for chunk in chunks
    ]
