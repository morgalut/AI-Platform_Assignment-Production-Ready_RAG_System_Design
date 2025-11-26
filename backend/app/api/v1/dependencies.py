# app/api/v1/dependencies.py

from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.auth.token_parser import parse_token
from app.config.connection import get_db
from app.rag.embedder import get_embedder
from app.rag.llm_client import get_llm_client
from app.orc.controller import ORCController


# ============================================================
# RBAC TOKEN DECODING
# ============================================================

def get_rbac_context(authorization: str | None = Header(default=None)):
    """
    Extract RBAC context from Authorization header.
    During early development, we fall back to mock-token mode.

    Expected header:
        Authorization: Bearer <token>

    parse_token() will decode either:
        - real JWT (future)
        - mock token (current)
    """

    if authorization is None:
        # fallback to mock mode
        return parse_token("mock-token")

    try:
        scheme, token = authorization.split(" ", 1)
        if scheme.lower() != "bearer":
            raise ValueError("Invalid auth scheme")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format",
        )

    return parse_token(token)


# ============================================================
# OPTIONAL RBAC HELPERS
# ============================================================

def require_role(required_role: str):
    """
    Dependency: ensures user contains the required user role.
    Usage:
        @router.post("/ingest", dependencies=[Depends(require_role("admin"))])
    """

    def wrapper(rbac_ctx=Depends(get_rbac_context)):
        roles = rbac_ctx.get("roles", [])
        if required_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required role: {required_role}",
            )
        return rbac_ctx

    return wrapper


def require_permission(required_perm: str):
    """
    Optional permission-based enforcement.
    If your token includes {"permissions": ["ingest:write"]}, this will work.

    Usage:
        dependencies=[Depends(require_permission("ingest:write"))]
    """

    def wrapper(rbac_ctx=Depends(get_rbac_context)):
        perms = rbac_ctx.get("permissions", [])
        if required_perm not in perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {required_perm}",
            )
        return rbac_ctx

    return wrapper


# ============================================================
# ORC CONTROLLER FACTORY
# ============================================================

def get_orc_controller(
    db: Session = Depends(get_db),
):
    """
    Builds the ORC Controller with DB + embedder + LLM client.
    """
    embedder = get_embedder()
    llm = get_llm_client()

    return ORCController(
        embedder=embedder,
        llm_client=llm,
        db=db,
    )
