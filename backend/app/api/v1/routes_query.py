# app/api/v1/routes_query.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.dependencies import (
    get_rbac_context,
    get_orc_controller,
    get_db,
)
from app.models.query import QueryRequest, QueryResponse

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query_endpoint(
    payload: QueryRequest,
    rbac_ctx=Depends(get_rbac_context),
    orc=Depends(get_orc_controller),
    db: Session = Depends(get_db),
):
    """
    Full RAG + ORC + ReAct pipeline:
    - Embed question
    - Retrieve relevant chunks through pgvector
    - Apply RBAC enforcement
    - Rank & summarize
    - Generate final answer via LLM
    - Return answer + citations
    """

    result = orc.run(
        question=payload.question,
        rbac_ctx=rbac_ctx,
    )

    return result
