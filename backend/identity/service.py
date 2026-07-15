from uuid import UUID

from datetime import datetime

from sqlalchemy.orm import Session

import models

from models import (

    Supplier,

    Client,

    UserIdentity,

    UserSession
)

from identity.session import (

    create_session,

    get_session
)


# =========================================================
# identity
# =========================================================

def get_or_create_identity(

    db: Session,

    phone: str
):

    identity = db.query(
        UserIdentity
    ).filter_by(
        phone=phone
    ).first()

    if identity:

        return identity

    identity = UserIdentity(
        phone=phone
    )

    db.add(identity)

    db.commit()

    db.refresh(identity)

    return identity


# =========================================================
# supplier register
# =========================================================

def register_supplier(

    db,

    phone,

    password,

    full_name,

    category_id,

    subcategory_id,

    location_id
):

    existing = db.query(
        Supplier
    ).filter_by(
        phone=phone
    ).first()

    if existing:

        return {

            "success": False,

            "error":
                "supplier_exists"
        }

    identity = get_or_create_identity(

        db,

        phone
    )

    supplier = Supplier(

        identity_id=identity.id,

        phone=phone,

        password=password,

        full_name=full_name,

        category_id=UUID(category_id),

        subcategory_id=UUID(subcategory_id),

        location_id=UUID(location_id)
    )

    db.add(supplier)

    db.commit()

    db.refresh(supplier)

    return {

        "success": True,

        "supplier": supplier
    }

# =========================================================
# ADMIN LOGIN
# =========================================================

def login_admin(
    db: Session,
    username: str,
    password: str,
):
    admin = (
        db.query(models.AdminUser)
        .filter_by(username=username)
        .first()
    )

    if not admin:
        return {
            "success": False,
            "error": "invalid_credentials",
        }

    if not admin.is_active:
        return {
            "success": False,
            "error": "admin_disabled",
        }

    # فعلاً برای سازگاری با داده‌های موجود.
    # در فاز Security Hardening باید تمام پسوردها Hash شوند.
    if str(admin.password) != str(password):
        return {
            "success": False,
            "error": "invalid_credentials",
        }

    identity = None

    if admin.identity_id:
        identity = (
            db.query(models.UserIdentity)
            .filter_by(id=admin.identity_id)
            .first()
        )

    if not identity:
        identity_phone = (
            f"admin:{admin.username}"
        )

        identity = (
            db.query(models.UserIdentity)
            .filter_by(phone=identity_phone)
            .first()
        )

    if not identity:
        identity = models.UserIdentity(
            phone=f"admin:{admin.username}",
        )

        db.add(identity)
        db.flush()

    if admin.identity_id != identity.id:
        admin.identity_id = identity.id

    admin.last_login_at = datetime.utcnow()

    db.flush()

    token = create_session(
        db=db,
        identity_id=identity.id,
        role="admin",
    )

    return {
        "success": True,
        "token": token,
        "admin": admin,
    }

# =========================================================
# supplier login
# =========================================================

def login_supplier(

    db,

    phone,

    password
):

    supplier = db.query(
        Supplier
    ).filter_by(
        phone=phone,
        password=password
    ).first()

    if not supplier:

        return {

            "success": False,

            "error":
                "invalid_credentials"
        }

    token = create_session(

        db,

        supplier.identity_id,

        "supplier"
    )

    return {

        "success": True,

        "token": token,

        "supplier": supplier
    }


# =========================================================
# CLIENT LOGIN
# =========================================================

def login_client(
    db: Session,
    phone: str,
):
    client = (
        db.query(models.Client)
        .filter_by(phone=phone)
        .first()
    )

    if not client:
        return {
            "success": False,
            "error": "client_not_found",
        }

    identity = None

    # Client از قبل Identity دارد
    if client.identity_id:
        identity = (
            db.query(models.UserIdentity)
            .filter_by(id=client.identity_id)
            .first()
        )

    # سازگاری با Clientهای قدیمی یا ساخته‌شده از مسیر Request
    if not identity:
        identity = (
            db.query(models.UserIdentity)
            .filter_by(phone=phone)
            .first()
        )

    # اولین Login: ساخت Identity
    if not identity:
        identity = models.UserIdentity(
            phone=phone,
        )

        db.add(identity)
        db.flush()

    # اتصال Client به Identity
    if client.identity_id != identity.id:
        client.identity_id = identity.id
        db.flush()

    token = create_session(
        db=db,
        identity_id=identity.id,
        role="client",
    )

    return {
        "success": True,
        "token": token,
        "client": client,
    }

# =========================================================
# token supplier
# =========================================================

def get_supplier_by_token(

    db,

    token
):

    session = get_session(
        db,
        token
    )

    if not session:

        return None

    if session.role != "supplier":

        return None

    return db.query(
        Supplier
    ).filter_by(
        identity_id=session.identity_id
    ).first()


# =========================================================
# token client
# =========================================================

def get_client_by_token(

    db,

    token
):

    session = get_session(
        db,
        token
    )

    if not session:

        return None

    if session.role != "client":

        return None

    return db.query(
        Client
    ).filter_by(
        identity_id=session.identity_id
    ).first()


# =========================================================
# logout
# =========================================================

def remove_session(

    db,

    token
):

    return db.query(
        UserSession
    ).filter_by(
        token=token
    ).delete()
