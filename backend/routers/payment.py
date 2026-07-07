from fastapi import (
    APIRouter,
    Depends,
    Header
)

from sqlalchemy.orm import Session

from database import get_db

from routers.auth import (
    get_supplier_by_token
)

from payments.service import (
    create_payment,
    verify_payment
)

router = APIRouter(
    prefix="/payment",
    tags=["payment"]
)


# =========================================================
# auth helper
# =========================================================

def auth(token: str):

    sid = get_supplier_by_token(token)

    if not sid:
        return None

    return sid


# =========================================================
# create payment
# =========================================================

@router.post("/create")
def payment_create(

    payload: dict,

    token: str = Header(None),

    db: Session = Depends(get_db)
):

    supplier_id = auth(token)

    if not supplier_id:

        return {
            "success": False,
            "error": "unauthorized"
        }

    amount = payload.get("amount")

    if not amount:

        return {
            "success": False,
            "error": "missing_amount"
        }

    return create_payment(

        db=db,

        supplier_id=supplier_id,

        amount=int(amount)
    )


# =========================================================
# verify payment
# =========================================================

@router.post("/verify")
def payment_verify(

    payload: dict,

    db: Session = Depends(get_db)
):

    authority = payload.get("authority")

    if not authority:

        return {
            "success": False,
            "error": "missing_authority"
        }

    return verify_payment(

        db=db,

        authority=authority
    )