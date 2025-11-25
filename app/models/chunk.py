# app/models/chunk.py

import uuid
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Integer, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.models.base import Base


class ChunkORM(Base):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(String, nullable=False)
    product_tag = Column(String, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)

    embedding = Column(Vector(384))                     # pgvector column
    meta = Column("metadata", JSONB)                    # avoid reserved name
    created_at = Column(TIMESTAMP, server_default=func.now())


class Chunk(BaseModel):
    id: str
    ticket_id: str
    product_tag: str
    chunk_index: int
    text: str

    metadata: Optional[Dict[str, Any]] = Field(default=None, alias="meta")

    class Config:
        from_attributes = True
        populate_by_name = True
