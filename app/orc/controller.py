# app/orc/controller.py

from typing import List, Dict, Any

from app.orc.reasoning_buffer import ReasoningBuffer
from app.orc.operator_registry import OperatorRegistry
from app.models.query import QueryResponse
from app.rag.retriever import chunks_to_used_chunks
from app.config.settings import get_settings

settings = get_settings()


class ORCController:
    """
    ORC = Operator – Reasoning – Controller

    Coordinates the ReAct-style flow:
    - Retrieve chunks
    - Apply RBAC filtering
    - Rank chunks
    - (Optionally) summarize
    - Generate final answer
    - Verify answer vs. retrieved evidence
    """

    def __init__(self, embedder, llm_client, db):
        self.embedder = embedder
        self.llm = llm_client
        self.db = db

        self.buffer = ReasoningBuffer()
        self.registry = OperatorRegistry()

        # How many chunks we allow into final context
        self.max_context_chunks = settings.orc_max_iterations

        self._load_operators()

    # ------------------------------------------------------------------
    # Operator registration
    # ------------------------------------------------------------------
    def _load_operators(self) -> None:
        """
        Register all operators once.
        """
        from app.orc.operators.retrieval_operator import RetrievalOperator
        from app.orc.operators.rbac_filter_operator import RBACFilterOperator
        from app.orc.operators.ranking_operator import RankingOperator
        from app.orc.operators.summarization_operator import SummarizationOperator
        from app.orc.operators.verification_operator import VerificationOperator
        from app.orc.operators.answer_operator import AnswerOperator

        self.registry.register("retrieval", RetrievalOperator(self.embedder, self.db))
        self.registry.register("rbac_filter", RBACFilterOperator())
        self.registry.register("ranking", RankingOperator())
        self.registry.register("summarization", SummarizationOperator(self.llm))
        self.registry.register("answer", AnswerOperator(self.llm))
        self.registry.register("verify", VerificationOperator())

    # ------------------------------------------------------------------
    # Internal helper to run operators
    # ------------------------------------------------------------------
    def _run_operator(self, name: str, *args, **kwargs):
        op = self.registry.get(name)
        if op is None:
            raise ValueError(f"Operator '{name}' is not registered")
        return op(*args, **kwargs)

    # ------------------------------------------------------------------
    # Public entrypoint
    # ------------------------------------------------------------------
    def run(self, question: str, rbac_ctx: Dict[str, Any]) -> QueryResponse:
        """
        Full ReAct-style RAG flow for a single question.
        """

        allowed_tags: List[str] = rbac_ctx.get("allowed_product_tags", []) or []

        # --- Step 0: RBAC sanity check --------------------------------
        if not allowed_tags:
            self.buffer.add("Thought: user has no allowed_product_tags; returning empty answer.")
            return QueryResponse(
                answer="You do not have access to any products, so no tickets can be used to answer this question.",
                source_ticket_ids=[],
                used_chunks=[],
                metadata={
                    "verified": True,
                    "retrieved_k": 0,
                    "filtered_k": 0,
                    "operator_sequence": [],
                },
            )

        # --- Step 1: Retrieval ----------------------------------------
        self.buffer.add("Thought: retrieve relevant chunks based on question and allowed product tags.")
        retrieved = self._run_operator("retrieval", question, allowed_tags)
        retrieved_count = len(retrieved)
        self.buffer.add(f"Observation: retrieved {retrieved_count} chunks from vector store.")

        if not retrieved:
            self.buffer.add("Thought: no chunks found; answer with 'no data' style response.")
            return QueryResponse(
                answer="I couldn't find any relevant resolved tickets to answer this question.",
                source_ticket_ids=[],
                used_chunks=[],
                metadata={
                    "verified": True,
                    "retrieved_k": 0,
                    "filtered_k": 0,
                    "operator_sequence": ["retrieval"],
                },
            )

        # --- Step 2: RBAC filter (defense-in-depth) -------------------
        filtered = self._run_operator("rbac_filter", retrieved, allowed_tags)
        filtered_count = len(filtered)
        self.buffer.add(f"Observation: {filtered_count} chunks remain after RBAC filtering.")

        if not filtered:
            self.buffer.add("Thought: RBAC filtering removed all chunks; user lacks access to retrieved tickets.")
            return QueryResponse(
                answer="Relevant tickets exist but are not accessible under your current permissions.",
                source_ticket_ids=[],
                used_chunks=[],
                metadata={
                    "verified": True,
                    "retrieved_k": retrieved_count,
                    "filtered_k": 0,
                    "operator_sequence": ["retrieval", "rbac_filter"],
                },
            )

        # --- Step 3: Ranking ------------------------------------------
        ranked = self._run_operator("ranking", filtered)
        self.buffer.add("Thought: ranked chunks by heuristic priority.")

        # Limit to configured max context size
        top_n = min(self.max_context_chunks, len(ranked))
        top_chunks = ranked[top_n * -1 :] if top_n > 0 else ranked  # or ranked[:top_n]
        # using [:top_n] is also fine — choose whichever better fits your retrieval style
        top_chunks = ranked[:top_n]

        # --- Step 4: Optional summarization ---------------------------
        # We can generate a quick internal summary for debugging/analysis
        # (not required for the final answer, but useful context).
        summary = self._run_operator("summarization", question, top_chunks)
        self.buffer.add("Observation: generated internal summary of retrieved context.")
        # Not returned to user; used only as part of reasoning buffer if needed.

        # --- Step 5: Answer synthesis ---------------------------------
        final_answer = self._run_operator("answer", question, top_chunks)
        self.buffer.add("Thought: produced final answer using LLM based on top chunks.")

        # --- Step 6: Verification -------------------------------------
        verified = self._run_operator("verify", final_answer, top_chunks)
        self.buffer.add(f"Observation: verification result = {verified}.")

        # --- Build response -------------------------------------------
        used_chunks = chunks_to_used_chunks(top_chunks)
        source_ticket_ids = list({c.ticket_id for c in top_chunks})

        metadata = {
            "verified": verified,
            "retrieved_k": retrieved_count,
            "filtered_k": filtered_count,
            "operator_sequence": self.registry.names(),
            # You *could* add a redacted reasoning trace here for internal logs only
            # "reasoning_trace": self.buffer.get_trace(),  # DON'T send this to end users in real prod
        }

        return QueryResponse(
            answer=final_answer,
            source_ticket_ids=source_ticket_ids,
            used_chunks=used_chunks,
            metadata=metadata,
        )
