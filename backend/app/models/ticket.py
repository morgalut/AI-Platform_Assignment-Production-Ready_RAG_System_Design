from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from sqlalchemy import (
    Column,
    String,
    TIMESTAMP,
    Text,
    ARRAY,
)
from app.models.base import Base


# ======================================================
# SQLAlchemy ORM Model
# ======================================================

class TicketORM(Base):
    __tablename__ = "tickets"

    ticket_id = Column(String, primary_key=True, index=True)
    product_tag = Column(String, nullable=False)

    customer_id = Column(String, nullable=True)
    customer_segment = Column(String, nullable=True)

    created_at = Column(TIMESTAMP, nullable=True)
    resolved_at = Column(TIMESTAMP, nullable=True)

    resolution_summary = Column(Text, nullable=True)

    tags = Column(ARRAY(String), nullable=True)

    language = Column(String, nullable=True, default="en")


# ======================================================
# Pydantic Model (Pydantic v2)
# ======================================================

class Ticket(BaseModel):
    ticket_id: str = Field(..., description="Unique support ticket ID")
    product_tag: str = Field(..., description="Product associated with ticket")

    customer_id: Optional[str] = Field(None, description="Customer unique ID")
    customer_segment: Optional[str] = Field(None, description="Customer business segment")

    created_at: Optional[datetime] = Field(None, description="Ticket creation timestamp")
    resolved_at: Optional[datetime] = Field(None, description="Ticket resolution timestamp")

    resolution_summary: Optional[str] = Field(
        None, description="Final resolution summary text"
    )

    tags: Optional[List[str]] = Field(
        None, description="List of tags/categories for the ticket"
    )

    language: Optional[str] = Field(
        "en", description="Language of the ticket content"
    )

    class Config:
        from_attributes = True  # Pydantic v2 replacement for orm_mode
