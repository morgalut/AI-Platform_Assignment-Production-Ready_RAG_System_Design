# app/orc/operators/ranking_operator.py

from typing import List
from app.models.chunk import ChunkORM


class RankingOperator:
    """
    Lightweight ranking based on:
    1. product tag grouping
    2. ticket recency (if available)
    3. chunk index (conversation order)
    """

    def __call__(self, chunks: List[ChunkORM]) -> List[ChunkORM]:
        if not chunks:
            return []

        return sorted(
            chunks,
            key=lambda c: (
                c.product_tag,
                getattr(c, "created_at", None) or 0,
                c.chunk_index,
            ),
        )
