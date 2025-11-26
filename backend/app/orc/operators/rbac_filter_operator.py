# app/orc/operators/rbac_filter_operator.py

from typing import List
from app.models.chunk import ChunkORM


class RBACFilterOperator:
    """
    Filters chunks by allowed product tags using set lookup for speed.
    """

    def __call__(self, chunks: List[ChunkORM], allowed_tags: list[str]) -> List[ChunkORM]:
        if not chunks or not allowed_tags:
            return []

        allowed = set(allowed_tags)
        return [c for c in chunks if c.product_tag in allowed]
