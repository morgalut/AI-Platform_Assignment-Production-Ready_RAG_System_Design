# app/orc/operators/verification_operator.py

from typing import List
from app.models.chunk import ChunkORM


class VerificationOperator:
    """
    Verifies that the answer:
    - only cites ticket_ids that were actually retrieved
    - does not hallucinate other IDs
    """

    def __call__(self, answer: str, chunks: List[ChunkORM]) -> bool:
        if not chunks:
            return True

        allowed_ids = {c.ticket_id for c in chunks}

        # Extract anything that looks like a ticket ID: TCK-12345
        cited = {
            tok
            for tok in answer.split()
            if tok.startswith("TCK-")
        }

        # All cited IDs must be from allowed_ids
        return cited.issubset(allowed_ids)
