from sqlalchemy import func

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query

from sqlalchemy.orm import Session

from database import get_db

from identity.dependencies import (
    admin_required
)

from models import (
    PaymentTransaction,
    WalletTransaction,
    CreditTransaction
)

router = APIRouter(
    prefix="/admin/payments",
    tags=["admin-payments"]
)


@router.get("")
def list_payments(
    status: str | None = Query(None),
    limit: int = Query(200, le=1000),
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    q = db.query(
        PaymentTransaction
    )

    if status:

        q = q.filter(
            PaymentTransaction.status == status
        )

    rows = (
        q.order_by(
            PaymentTransaction.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    return {

        "success": True,

        "items": [

            {

                "id":
                    str(x.id),

                "supplier_id":
                    str(x.supplier_id),

                "amount":
                    x.amount,

                "gateway":
                    x.gateway,

                "status":
                    x.status,

                "authority":
                    x.authority,

                "ref_id":
                    x.ref_id,

                "created_at":
                    x.created_at,

                "paid_at":
                    x.paid_at
            }

            for x in rows
        ]
    }


@router.get("/summary")
def payment_summary(
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    paid_volume = (
        db.query(
            func.coalesce(
                func.sum(
                    PaymentTransaction.amount
                ),
                0
            )
        )
        .filter(
            PaymentTransaction.status == "paid"
        )
        .scalar()
    )

    payment_count = db.query(
        PaymentTransaction
    ).count()

    wallet_volume = (
        db.query(
            func.coalesce(
                func.sum(
                    WalletTransaction.amount
                ),
                0
            )
        ).scalar()
    )

    credit_volume = (
        db.query(
            func.coalesce(
                func.sum(
                    CreditTransaction.amount
                ),
                0
            )
        ).scalar()
    )

    return {

        "success": True,

        "payment_count":
            payment_count,

        "paid_volume":
            paid_volume,

        "wallet_volume":
            wallet_volume,

        "credit_volume":
            credit_volume
    }


@router.get("/{payment_id}")
def payment_details(
    payment_id: str,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    row = db.query(
        PaymentTransaction
    ).filter(
        PaymentTransaction.id == payment_id
    ).first()

    if not row:

        return {
            "success": False,
            "error": "payment_not_found"
        }

    return {

        "success": True,

        "payment": {

            "id":
                str(row.id),

            "supplier_id":
                str(row.supplier_id),

            "amount":
                row.amount,

            "gateway":
                row.gateway,

            "authority":
                row.authority,

            "status":
                row.status,

            "ref_id":
                row.ref_id,

            "failure_reason":
                row.failure_reason,

            "verify_payload":
                row.verify_payload,

            "created_at":
                row.created_at,

            "paid_at":
                row.paid_at
        }
    }
