# app/orc/operators/answer_operator.py

from typing import List
from app.models.chunk import ChunkORM


class AnswerOperator:
    """
    Combines question + selected chunks and produces a final answer.
    Designed to minimize LLM prompt size and maximize clarity.
    """

    MAX_CONTEXT_CHARS = 8000  # prevents long-ticket overload

    def __init__(self, llm_client):
        self.llm = llm_client

    def _build_context(self, chunks: List[ChunkORM]) -> str:
        # Efficient join and truncation
        context = "\n".join(c.text for c in chunks)
        return context[: self.MAX_CONTEXT_CHARS]

    def __call__(self, question: str, chunks: List[ChunkORM]) -> str:
        context = self._build_context(chunks)
        ticket_ids = {c.ticket_id for c in chunks}

        prompt = (
            "You are an expert support system assistant.\n\n"
            f"User question:\n{question}\n\n"
            f"Relevant ticket excerpts:\n{context}\n\n"
            f"Tickets referenced: {', '.join(ticket_ids)}\n\n"
            "Provide a precise, accurate answer based ONLY on these tickets. "
            "Cite ticket IDs explicitly in your answer."
        )

        return self.llm.generate(prompt)
