# app/ingestion/loader.py

import json
from pathlib import Path
from typing import List

from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.models.ticket import Ticket, TicketORM

settings = get_settings()


def load_tickets_from_file(path: str | Path | None = None) -> List[Ticket]:
    """
    Load mock tickets from a JSON file and return them as Pydantic Ticket models.

    Expected JSON format:
    [
      {
        "ticket_id": "...",
        "product_tag": "Product_A",
        "customer_id": "...",
        "customer_segment": "...",
        "created_at": "...",
        "resolved_at": "...",
        "resolution_summary": "...",
        "tags": ["crash", "save"],
        "language": "en"
      },
      ...
    ]
    """
    if path is None:
        path = settings.data_path

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Ticket data file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    tickets: List[Ticket] = []
    for item in raw:
        tickets.append(Ticket(**item))

    return tickets


def upsert_tickets(db: Session, tickets: List[Ticket]) -> None:
    """
    Insert or update Ticket rows in the 'tickets' table.
    """
    for t in tickets:
        # Check if ticket already exists
        existing = db.query(TicketORM).filter_by(ticket_id=t.ticket_id).first()
        if existing:
            # Update basic fields (optional: expand as needed)
            existing.product_tag = t.product_tag
            existing.customer_id = t.customer_id
            existing.customer_segment = t.customer_segment
            existing.created_at = t.created_at
            existing.resolved_at = t.resolved_at
            existing.resolution_summary = t.resolution_summary
            existing.tags = t.tags
            existing.language = t.language
        else:
            db.add(
                TicketORM(
                    ticket_id=t.ticket_id,
                    product_tag=t.product_tag,
                    customer_id=t.customer_id,
                    customer_segment=t.customer_segment,
                    created_at=t.created_at,
                    resolved_at=t.resolved_at,
                    resolution_summary=t.resolution_summary,
                    tags=t.tags,
                    language=t.language,
                )
            )
    db.commit()
