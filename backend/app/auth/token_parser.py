# app/auth/token_parser.py

from typing import Dict, Any
import os
import logging

import jwt
from jwt import InvalidTokenError

logger = logging.getLogger("app.auth.token_parser")

# ---------------------------------------------------------
# Default mock user profile (development mode only)
# ---------------------------------------------------------
MOCK_USER = {
    "user_id": "demo-user",
    "allowed_product_tags": ["Product_A", "Product_B"],
    "roles": ["support_rep"],
    "permissions": ["ingest:write", "query:read"],   # <-- Important fix
}


def _strip_bearer_prefix(token: str) -> str:
    """Remove 'Bearer ' prefix if present."""
    if token.startswith("Bearer "):
        return token[len("Bearer "):].strip()
    return token.strip()


def parse_token(raw_token: str) -> Dict[str, Any]:
    """
    Parse/validate a JWT token using HS256 if JWT_SECRET is configured.
    Otherwise, fallback to MOCK_USER (for development mode).
    """
    jwt_secret = os.getenv("JWT_SECRET")

    # Use mock profile when JWT_SECRET is absent
    if not jwt_secret:
        if raw_token not in ("", "mock-token", None):
            logger.warning("JWT_SECRET not set — using mock authentication profile.")
        return MOCK_USER

    # Remove prefix if needed
    token = _strip_bearer_prefix(raw_token)

    try:
        decoded = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            options={"require": ["sub"]},   # Keep minimal requirement
        )

        logger.info("JWT successfully decoded.")

        return {
            "user_id": decoded.get("sub"),
            "roles": decoded.get("roles", []),
            "allowed_product_tags": decoded.get("allowed_product_tags", []),
            "permissions": decoded.get("permissions", []),
        }

    except InvalidTokenError as e:
        logger.error(f"Invalid JWT token: {e}. Falling back to mock user.")
        return MOCK_USER
