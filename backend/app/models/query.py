from typing import List, Optional, Dict, Any
from pydantic import BaseModel


# ======================================================
# Request Model
# ======================================================

class QueryRequest(BaseModel):
    question: str
    max_context_chunks: int = 5


# ======================================================
# Used chunk metadata in response
# ======================================================

class UsedChunk(BaseModel):
    ticket_id: str
    product_tag: str
    chunk_index: int
    text: str


# ======================================================
# Response Model
# ======================================================

class QueryResponse(BaseModel):
    answer: str
    source_ticket_ids: List[str]
    used_chunks: List[UsedChunk]
    metadata: Dict[str, Any]
