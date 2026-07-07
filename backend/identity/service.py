from uuid import UUID

from sqlalchemy.orm import Session

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
# client login
# =========================================================

def login_client(

    db,

    phone
):

    client = db.query(
        Client
    ).filter_by(
        phone=phone
    ).first()

    if not client:

        identity = get_or_create_identity(

            db,

            phone
        )

        client = Client(

            identity_id=identity.id,

            phone=phone
        )

        db.add(client)

        db.commit()

        db.refresh(client)

    token = create_session(

        db,

        client.identity_id,

        "client"
    )

    return {

        "success": True,

        "token": token,

        "client": client
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
