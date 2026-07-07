from fastapi import (
    APIRouter,
    Depends,
    Header
)

from sqlalchemy.orm import Session

from database import get_db

from models import (
    Supplier,
    Client
)

from otp.service import (
    verify_otp
)

from identity.service import (

    register_supplier,

    login_supplier,

    login_client,

    remove_session,

    get_supplier_by_token,

    get_client_by_token
)

router = APIRouter(

    prefix="/auth",

    tags=["auth"]
)


# =========================================================
# SUPPLIER REGISTER
# =========================================================

@router.post("/supplier/register")
def supplier_register(

    payload: dict,

    db: Session = Depends(get_db)
):

    required = [

        "phone",

        "password",

        "full_name",

        "category_id",

        "subcategory_id",

        "location_id"
    ]

    for field in required:

        if not payload.get(field):

            return {

                "success": False,

                "error":
                    f"missing_{field}"
            }

    result = register_supplier(

        db=db,

        phone=
            payload["phone"],

        password=
            payload["password"],

        full_name=
            payload["full_name"],

        category_id=
            payload["category_id"],

        subcategory_id=
            payload["subcategory_id"],

        location_id=
            payload["location_id"]
    )

    if not result["success"]:
        return result

    supplier = result["supplier"]

    return {

        "success": True,

        "supplier": {

            "id":
                str(supplier.id),

            "phone":
                supplier.phone,

            "name":
                supplier.full_name
        }
    }


# =========================================================
# SUPPLIER LOGIN
# =========================================================

@router.post("/supplier/login")
def supplier_login(

    payload: dict,

    db: Session = Depends(get_db)
):

    phone = payload.get(
        "phone"
    )

    password = payload.get(
        "password"
    )

    if not phone or not password:

        return {

            "success": False,

            "error":
                "missing_fields"
        }

    result = login_supplier(

        db,

        phone,

        password
    )

    if not result["success"]:
        return result

    supplier = result["supplier"]

    return {

        "success": True,

        "token":
            result["token"],

        "supplier": {

            "id":
                str(supplier.id),

            "phone":
                supplier.phone,

            "name":
                supplier.full_name,

            "credit_balance":
                supplier.credit_balance,

            "wallet_balance":
                supplier.wallet_balance
        }
    }


# =========================================================
# CLIENT LOGIN
# =========================================================

@router.post("/client/login")
def client_login(

    payload: dict,

    db: Session = Depends(get_db)
):

    phone = payload.get(
        "phone"
    )

    code = payload.get(
        "code"
    )

    if not phone or not code:

        return {

            "success": False,

            "error":
                "missing_fields"
        }

    if not verify_otp(
        phone,
        code
    ):

        return {

            "success": False,

            "error":
                "invalid_otp"
        }

    result = login_client(

        db,

        phone
    )

    client = result["client"]

    return {

        "success": True,

        "token":
            result["token"],

        "client": {

            "id":
                str(client.id),

            "phone":
                client.phone,

            "name":
                client.full_name
        }
    }


# =========================================================
# CURRENT SUPPLIER
# =========================================================

@router.get("/supplier/me")
def current_supplier(

    token: str = Header(None),

    db: Session = Depends(get_db)
):

    supplier = get_supplier_by_token(

        db,

        token
    )

    if not supplier:

        return {

            "success": False
        }

    return {

        "success": True,

        "supplier": {

            "id":
                str(supplier.id),

            "phone":
                supplier.phone,

            "name":
                supplier.full_name,

            "credit_balance":
                supplier.credit_balance,

            "wallet_balance":
                supplier.wallet_balance
        }
    }


# =========================================================
# CURRENT CLIENT
# =========================================================

@router.get("/client/me")
def current_client(

    token: str = Header(None),

    db: Session = Depends(get_db)
):

    client = get_client_by_token(

        db,

        token
    )

    if not client:

        return {

            "success": False
        }

    return {

        "success": True,

        "client": {

            "id":
                str(client.id),

            "phone":
                client.phone,

            "name":
                client.full_name
        }
    }


# =========================================================
# LOGOUT
# =========================================================

@router.post("/logout")
def logout(

    token: str = Header(None),

    db: Session = Depends(get_db)
):

    remove_session(

        db,

        token
    )

    db.commit()

    return {

        "success": True
    }

# =========================================================
# BACKWARD COMPATIBILITY
# =========================================================

def get_supplier_id_by_token(

    token,

    db
):

    supplier = get_supplier_by_token(

        db,

        token
    )

    if not supplier:
        return None

    return str(
        supplier.id
    )


def get_client_id_by_token(

    token,

    db
):

    client = get_client_by_token(

        db,

        token
    )

    if not client:
        return None

    return str(
        client.id
    )