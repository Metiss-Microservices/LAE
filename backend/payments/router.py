from fastapi import (
    APIRouter,
    Depends,
    Header
)

from sqlalchemy.orm import Session

from database import get_db

from identity.dependencies import (
    get_current_supplier
)

from payments.service import (
    create_payment,
    verify_payment,
    get_payment,
    get_supplier_payments
)

import models


router = APIRouter(
    prefix="/payments",
    tags=["payments"]
)


# =========================================================
# CREATE PAYMENT
# =========================================================

@router.post("/create")
def create_payment_endpoint(
    payload: dict,
    supplier=Depends(
        get_current_supplier
    ),
    db: Session = Depends(get_db)
):

    amount = int(
        payload.get(
            "amount",
            0
        )
    )

    return create_payment(
        db=db,
        supplier_id=supplier.id,
        amount=amount
    )


# =========================================================
# VERIFY MANUAL
# =========================================================

@router.post("/verify")
def verify_manual(
    payload: dict,
    supplier=Depends(
        get_current_supplier
    ),
    db: Session = Depends(get_db)
):

    authority = payload.get(
        "authority"
    )

    if not authority:

        return {
            "success": False,
            "error":
                "missing_authority"
        }

    return verify_payment(
        db=db,
        authority=authority
    )


# =========================================================
# SINGLE PAYMENT
# =========================================================

@router.get("/{payment_id}")
def payment_details(
    payment_id: str,
    supplier=Depends(
        get_current_supplier
    ),
    db: Session = Depends(get_db)
):

    result = get_payment(
        db,
        payment_id
    )

    if not result.get(
        "success"
    ):
        return result

    payment = result["payment"]

    if str(
        payment["supplier_id"]
    ) != str(
        supplier.id
    ):

        return {
            "success": False,
            "error":
                "access_denied"
        }

    return result


# =========================================================
# MY PAYMENTS
# =========================================================

@router.get("/")
def my_payments(
    supplier=Depends(
        get_current_supplier
    ),
    db: Session = Depends(get_db)
):

    return {
        "success": True,
        "payments":
            get_supplier_payments(
                db,
                supplier.id
            )
    }


# =========================================================
# PAYMENT STATS
# =========================================================

@router.get("/stats/me")
def my_payment_stats(
    supplier=Depends(
        get_current_supplier
    ),
    db: Session = Depends(get_db)
):

    payments = db.query(
        models.PaymentTransaction
    ).filter_by(
        supplier_id=supplier.id,
        status="paid"
    ).all()

    total_paid = sum(
        p.amount
        for p in payments
    )

    return {
        "success": True,
        "count": len(payments),
        "total_paid": total_paid
    }