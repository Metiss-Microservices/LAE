from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from datetime import datetime

from database import get_db

from models import (
    Supplier,
    WalletTransaction
)

router = APIRouter(
    prefix="/billing"
)


# =========================================================
# charge supplier
# =========================================================

@router.post("/charge")
def charge_supplier(
    supplier_id: str,
    amount: int,
    db: Session = Depends(get_db)
):

    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id
    ).first()

    if not supplier:

        return {
            "success": False,
            "error": "supplier_not_found"
        }

    if amount <= 0:

        return {
            "success": False,
            "error": "invalid_amount"
        }

    supplier.credit_balance += amount

    tx = WalletTransaction(

        supplier_id=supplier.id,

        amount=amount,

        type="charge",

        status="success",

        authority="-",

        created_at=datetime.utcnow()
    )

    db.add(tx)

    db.commit()

    return {

        "success": True,

        "new_credit":
            supplier.credit_balance
    }


# =========================================================
# get credit
# =========================================================

@router.get("/credit")
def get_credit(
    supplier_id: str,
    db: Session = Depends(get_db)
):

    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id
    ).first()

    if not supplier:

        return {
            "success": False,
            "error": "supplier_not_found"
        }

    return {

        "success": True,

        "credit":
            supplier.credit_balance
    }


# =========================================================
# transactions
# =========================================================

@router.get("/transactions")
def get_transactions(
    supplier_id: str,
    db: Session = Depends(get_db)
):

    txs = db.query(
        WalletTransaction
    ).filter(

        WalletTransaction.supplier_id
        == supplier_id

    ).order_by(

        WalletTransaction.created_at.desc()

    ).all()

    return {

        "success": True,

        "transactions": [

            {

                "id":
                    str(t.id),

                "amount":
                    t.amount,

                "type":
                    t.type,

                "status":
                    t.status,

                "authority":
                    t.authority,

                "created_at":
                    str(t.created_at)

            }

            for t in txs
        ]
    }