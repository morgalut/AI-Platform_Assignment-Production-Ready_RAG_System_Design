# app/orc/operators/summarization_operator.py

from typing import List
from app.models.chunk import ChunkORM


class SummarizationOperator:
    """
    Summarizes retrieved chunks into a compact digest.
    """

    MAX_CONTEXT_CHARS = 6000

    def __init__(self, llm_client):
        self.llm = llm_client

    def __call__(self, question: str, chunks: List[ChunkORM]) -> str:
        if not chunks:
            return ""

        context = "\n".join(c.text for c in chunks)
        context = context[: self.MAX_CONTEXT_CHARS]

        prompt = (
            "Summarize the following support ticket information into a concise "
            "technical digest that a support engineer can use:\n\n"
            f"{context}"
        )

        return self.llm.generate(prompt)
