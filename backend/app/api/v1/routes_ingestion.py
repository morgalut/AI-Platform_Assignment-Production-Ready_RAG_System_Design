# app/api/v1/routes_ingestion.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_db, require_permission
from app.ingestion.embed_and_index import run_ingestion

router = APIRouter()


@router.post("/ingest", summary="Trigger ingestion pipeline")
def ingest_data(
    db: Session = Depends(get_db),
    _ = Depends(require_permission("ingest:write")),
):
    """
    Load tickets -> chunk -> embed -> store in pgvector.
    Requires 'ingest:write' permission.
    """
    inserted = run_ingestion(db=db)
    return {
        "status": "ok",
        "message": "Ingestion completed successfully.",
        "inserted_chunks": inserted,
    }
