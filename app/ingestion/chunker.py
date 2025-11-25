# app/ingestion/chunker.py

from typing import List, Dict, Any
from app.config.settings import get_settings
from app.models.ticket import Ticket

settings = get_settings()


def split_text_into_chunks(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Simple character-based chunking with overlap.
    This is naive but fine for the assignment and small data.
    """
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + chunk_size, length)
        chunks.append(text[start:end])
        if end == length:
            break
        start = end - overlap  # move back by overlap for the next chunk

    return chunks


def make_chunks_for_ticket(
    ticket: Ticket,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> List[Dict[str, Any]]:
    """
    Build chunk payloads from a single Ticket.

    Returns a list of dicts describing each chunk:
    {
      "ticket_id": ...,
      "product_tag": ...,
      "chunk_index": ...,
      "text": ...,
      "metadata": {...}
    }
    """
    if chunk_size is None:
        chunk_size = settings.chunk_size
    if overlap is None:
        overlap = settings.chunk_overlap

    chunks: List[Dict[str, Any]] = []

    # For now, we only chunk the resolution_summary.
    # You can later extend with conversation, tags, etc.
    summary_text = ticket.resolution_summary or ""
    text_chunks = split_text_into_chunks(summary_text, chunk_size, overlap)

    for idx, chunk_text in enumerate(text_chunks):
        chunks.append(
            {
                "ticket_id": ticket.ticket_id,
                "product_tag": ticket.product_tag,
                "chunk_index": idx,
                "text": chunk_text,
                "metadata": {
                    "source_type": "resolution_summary",
                    "customer_segment": ticket.customer_segment,
                    "language": ticket.language,
                    "tags": ticket.tags,
                },
            }
        )

    return chunks
