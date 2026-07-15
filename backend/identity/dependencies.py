# identity/dependencies.py

from datetime import datetime

from fastapi import (
    Depends,
    Header,
    HTTPException,
)

from sqlalchemy.orm import Session

import models

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
    return get_supplier_by_token(
        db,
        token,
    )


def get_current_supplier(
    token: str = Header(None),
    db: Session = Depends(get_db),
):
    if not token:
        raise HTTPException(
            status_code=401,
            detail="supplier_token_required",
        )

    supplier = get_supplier_by_token(
        db,
        token,
    )

    if not supplier:
        raise HTTPException(
            status_code=401,
            detail="invalid_supplier_token",
        )

    return supplier

# =========================================================
# CLIENT AUTH
# =========================================================

def client_auth(
    token: str = Header(None),
    db: Session = Depends(get_db),
):
    return get_client_by_token(
        db,
        token,
    )


def get_current_client(
    token: str = Header(None),
    db: Session = Depends(get_db),
):
    return client_auth(
        token=token,
        db=db,
    )


# =========================================================
# ADMIN AUTH
# =========================================================

def admin_required(
    token: str = Header(None),
    db: Session = Depends(get_db),
):
    if not token:
        raise HTTPException(
            status_code=401,
            detail="admin_token_required",
        )

    session = (
        db.query(models.UserSession)
        .filter(
            models.UserSession.token == token,
            models.UserSession.role == "admin",
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=401,
            detail="invalid_admin_token",
        )

    if (
        session.expires_at
        and session.expires_at <= datetime.utcnow()
    ):
        raise HTTPException(
            status_code=401,
            detail="admin_session_expired",
        )

    admin = (
        db.query(models.AdminUser)
        .filter(
            models.AdminUser.identity_id
            == session.identity_id,
            models.AdminUser.is_active.is_(True),
        )
        .first()
    )

    if not admin:
        raise HTTPException(
            status_code=403,
            detail="admin_access_denied",
        )

    return admin


def get_current_admin(
    token: str = Header(None),
    db: Session = Depends(get_db),
):
    return admin_required(
        token=token,
        db=db,
    )


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