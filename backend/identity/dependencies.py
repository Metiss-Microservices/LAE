# identity/dependencies.py

from fastapi import Depends
from fastapi import Header

from sqlalchemy.orm import Session

from database import get_db

from identity.service import (
    get_supplier_by_token,
    get_client_by_token,
)


# =========================================================
# SUPPLIER AUTH
# =========================================================

def supplier_auth(
    token: str = Header(None),
    db: Session = Depends(get_db),
):
    return get_supplier_by_token(db, token)


# Backward compatibility
def get_current_supplier(
    token: str = Header(None),
    db: Session = Depends(get_db),
):
    return supplier_auth(token=token, db=db)


# =========================================================
# CLIENT AUTH
# =========================================================

def client_auth(
    token: str = Header(None),
    db: Session = Depends(get_db),
):
    return get_client_by_token(db, token)


# Backward compatibility
def get_current_client(
    token: str = Header(None),
    db: Session = Depends(get_db),
):
    return client_auth(token=token, db=db)

# =========================================================
# ADMIN AUTH (Temporary compatibility)
# =========================================================

def admin_required():
    """
    Temporary compatibility dependency.

    Phase 1:
    Only keeps routers importable.
    Real admin authentication will be implemented later.
    """
    return {
        "id": "system",
        "role": "admin",
    }

def get_current_admin():
    """
    Temporary compatibility stub.
    """
    return {"role": "admin"}

# =========================================================
# EXPORTS
# =========================================================

__all__ = [
    "supplier_auth",
    "client_auth",
    "get_current_supplier",
    "get_current_client",
    "admin_required",
    "get_current_admin",
]

