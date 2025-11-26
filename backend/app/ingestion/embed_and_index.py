# app/ingestion/embed_and_index.py

from typing import List, Callable, Sequence, Optional

from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.config.connection import SessionLocal

from app.ingestion.loader import load_tickets_from_file, upsert_tickets
from app.ingestion.chunker import make_chunks_for_ticket

from app.models.ticket import Ticket
from app.models.chunk import ChunkORM

from app.rag.embedder import get_embedder

settings = get_settings()


# --------------------------------------------------------------------------------------
# PUBLIC INGESTION ENTRY POINT
# --------------------------------------------------------------------------------------

def run_ingestion(
    db: Optional[Session] = None,
    embedder: Optional[Callable[[Sequence[str]], List[List[float]]]] = None,
    external_records: Optional[list] = None,
    data_path: Optional[str] = None,
) -> int:
    """
    Flexible ingestion entry point:
    - If external_records provided → ingest uploaded JSON
    - Else if data_path provided → ingest from a specific file path
    - Else → ingest from default (settings.data_path)

    Returns:
        int: number of inserted chunks.
    """

    close_db_at_end = False

    # Ensure DB session
    if db is None:
        db = SessionLocal()
        close_db_at_end = True

    # Load embedder instance
    if embedder is None:
        embed_instance = get_embedder()

        def embedder(texts: Sequence[str]) -> List[List[float]]:
            return embed_instance.embed(texts)

    try:
        # MODE 1 — Uploaded JSON
        if external_records is not None:
            return ingest_uploaded_records(db, embedder, external_records)

        # MODE 2 — Custom ingestion path
        if data_path is not None:
            return ingest_file_path(db, embedder, data_path)

        # MODE 3 — Default ingestion path
        return ingest_file_path(db, embedder, settings.data_path)

    finally:
        if close_db_at_end:
            db.close()


# --------------------------------------------------------------------------------------
# INGESTION MODES
# --------------------------------------------------------------------------------------

def ingest_uploaded_records(
    db: Session,
    embedder: Callable[[Sequence[str]], List[List[float]]],
    records: list,
) -> int:
    """
    Ingest from uploaded JSON (list of ticket-like objects).
    Automatically maps common fields to Ticket ORM attributes.
    """

    tickets: List[Ticket] = []

    for idx, r in enumerate(records):
        try:
            ticket = Ticket(
                ticket_id=str(
                    r.get("ticket_id")
                    or r.get("id")
                    or r.get("ticketId")
                    or f"uploaded-{idx}"
                ),
                summary=(
                    r.get("summary")
                    or r.get("title")
                    or r.get("subject")
                    or r.get("description")
                    or r.get("body")
                    or r.get("text")
                    or ""
                ),
                resolution=(
                    r.get("resolution")
                    or r.get("fix")
                    or r.get("answer")
                    or r.get("response")
                    or ""
                ),
                product_tag=(
                    r.get("product_tag")
                    or r.get("product")
                    or r.get("category")
                    or "Unknown"
                ),
            )

            tickets.append(ticket)

        except Exception as e:
            print(f"[WARN] Skipping invalid record index={idx}: {e}")

    print(f"[INGEST] Loaded {len(tickets)} tickets from uploaded JSON")

    if not tickets:
        print("[INGEST] No usable tickets found in uploaded file.")
        return 0

    return _ingest_ticket_list(db, embedder, tickets, mode="uploaded-json")


def ingest_file_path(
    db: Session,
    embedder: Callable[[Sequence[str]], List[List[float]]],
    data_path: str
) -> int:
    """Ingest from a file path (default or specified)."""
    tickets = load_tickets_from_file(path=data_path)
    print(f"[INGEST] Loaded {len(tickets)} tickets from disk: {data_path}")
    return _ingest_ticket_list(db, embedder, tickets, mode=f"file:{data_path}")


# --------------------------------------------------------------------------------------
# CORE SHARED INGESTION ROUTINE
# --------------------------------------------------------------------------------------

def _ingest_ticket_list(
    db: Session,
    embedder: Callable[[Sequence[str]], List[List[float]]],
    tickets: List[Ticket],
    mode: str,
) -> int:
    """
    Shared ingestion routine for:
        - uploaded JSON
        - file-based ingestion
    Includes:
        1) Upsert tickets
        2) Chunk summary/resolution
        3) Embed chunks
        4) Insert chunks into pgvector
    """

    print(f"[INGEST] Starting ingestion mode: {mode}")
    print(f"[INGEST] Tickets received: {len(tickets)}")

    # 1. UPSERT TICKETS into DB
    upsert_tickets(db, tickets)

    # 2. CHUNKING
    all_chunks = []
    for t in tickets:
        # make_chunks_for_ticket uses summary/resolution internally
        chunks = make_chunks_for_ticket(t)
        all_chunks.extend(chunks)

    print(f"[INGEST] Total chunks produced: {len(all_chunks)}")

    if not all_chunks:
        print("[INGEST] WARNING: No chunks generated — check ticket content mapping.")
        return 0

    # 3. EMBEDDING
    texts = [c["text"] for c in all_chunks]
    embeddings = embedder(texts)

    if len(embeddings) != len(all_chunks):
        raise ValueError(
            f"Embedding mismatch: {len(embeddings)} embeddings vs {len(all_chunks)} chunks"
        )

    # 4. INSERT CHUNKS
    for payload, emb_vector in zip(all_chunks, embeddings):
        chunk_row = ChunkORM(
            ticket_id=payload["ticket_id"],
            product_tag=payload["product_tag"],
            chunk_index=payload["chunk_index"],
            text=payload["text"],
            embedding=emb_vector,
            metadata=payload["metadata"],
        )
        db.add(chunk_row)

    db.commit()

    print(
        f"[INGEST] Completed mode={mode}: "
        f"{len(tickets)} tickets → {len(all_chunks)} chunks inserted."
    )

    return len(all_chunks)
