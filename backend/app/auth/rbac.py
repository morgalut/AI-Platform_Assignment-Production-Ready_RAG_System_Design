# app/auth/rbac.py

from typing import List, Set


# ---------------------------------------------------------------------
# Role → Permission Mapping (central policy definition)
# ---------------------------------------------------------------------
ROLE_PERMISSIONS = {
    "admin": {
        "query:read",
        "ingest:write",
        "tickets:read",
    },
    "support_rep": {
        "query:read",
        "tickets:read",
    },
    "viewer": {
        "query:read",
    },
}


def get_permissions_for_roles(roles: List[str]) -> Set[str]:
    """
    Expand user roles into a set of permissions.
    Unknown roles are ignored.
    """
    perms = set()
    for role in roles:
        perms.update(ROLE_PERMISSIONS.get(role, set()))
    return perms


# ---------------------------------------------------------------------
# Permission check
# ---------------------------------------------------------------------
def require_permission(user_permissions: Set[str], required: str) -> bool:
    """
    Return True if user_permissions include the required permission.
    """
    return required in user_permissions


# ---------------------------------------------------------------------
# Product-based filtering
# ---------------------------------------------------------------------
def has_access(product_tag: str, allowed_product_tags: List[str]) -> bool:
    """
    Efficient membership check using sets.
    """
    return product_tag in set(allowed_product_tags)
