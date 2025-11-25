# app/ingestion/embed_and_index.py

from typing import List, Callable, Sequence

from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.config.connection import SessionLocal
from app.ingestion.loader import load_tickets_from_file, upsert_tickets
from app.ingestion.chunker import make_chunks_for_ticket
from app.models.ticket import Ticket
from app.models.chunk import ChunkORM
from app.rag.embedder import get_embedder  # <-- NEW

settings = get_settings()


def run_ingestion(
    db: Session | None = None,
    embedder: Callable[[Sequence[str]], List[List[float]]] | None = None,
    data_path: str | None = None,
) -> None:
    """
    End-to-end ingestion:
    - Load tickets from JSON
    - Upsert into tickets table
    - Chunk resolution summaries
    - Embed chunks
    - Insert into chunks table
    """
    # Ensure we have a DB session
    close_db_at_end = False
    if db is None:
        db = SessionLocal()
        close_db_at_end = True

    # Use provided embedder or global default
    if embedder is None:
        embedder_instance = get_embedder()

        def embedder(texts: Sequence[str]) -> List[List[float]]:
            return embedder_instance.embed(texts)

    try:
        # 1) Load
        tickets: List[Ticket] = load_tickets_from_file(path=data_path)

        # 2) Upsert tickets
        upsert_tickets(db, tickets)

        # 3) Build chunks
        all_chunk_payloads = []
        for ticket in tickets:
            chunk_payloads = make_chunks_for_ticket(ticket)
            all_chunk_payloads.extend(chunk_payloads)

        if not all_chunk_payloads:
            print("No chunks produced from tickets.")
            return

        # 4) Embed texts
        texts = [c["text"] for c in all_chunk_payloads]
        embeddings = embedder(texts)

        if len(embeddings) != len(all_chunk_payloads):
            raise ValueError("Number of embeddings does not match number of chunks")

        # 5) Insert into chunks table
        for payload, emb in zip(all_chunk_payloads, embeddings):
            chunk_row = ChunkORM(
                ticket_id=payload["ticket_id"],
                product_tag=payload["product_tag"],
                chunk_index=payload["chunk_index"],
                text=payload["text"],
                embedding=emb,
                metadata=payload["metadata"],
            )
            db.add(chunk_row)

        db.commit()
        print(f"Ingestion complete: {len(tickets)} tickets, {len(all_chunk_payloads)} chunks.")

    finally:
        if close_db_at_end:
            db.close()
