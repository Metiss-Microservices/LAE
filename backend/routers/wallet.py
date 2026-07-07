from fastapi import (
    APIRouter,
    Depends,
    Header
)

from sqlalchemy.orm import Session

from database import get_db

from models import (
    Supplier,
    WalletTransaction
)

from routers.auth import (
    get_supplier_by_token
)

router = APIRouter(
    prefix="/wallet"
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
# balance
# =========================================================

@router.get("/balance")
def balance(
    token: str = Header(None),
    db: Session = Depends(get_db)
):

    supplier_id = auth(token)

    if not supplier_id:

        return {
            "success": False,
            "error": "unauthorized"
        }

    supplier = db.query(Supplier).filter_by(
        id=supplier_id
    ).first()

    if not supplier:

        return {
            "success": False,
            "error": "supplier_not_found"
        }

    return {

        "success": True,

        "wallet_balance":
            supplier.wallet_balance or 0,

        "credit_balance":
            supplier.credit_balance or 0
    }


# =========================================================
# transactions
# =========================================================

@router.get("/transactions")
def transactions(
    token: str = Header(None),
    db: Session = Depends(get_db)
):

    supplier_id = auth(token)

    if not supplier_id:

        return {
            "success": False,
            "error": "unauthorized"
        }

    txs = db.query(
        WalletTransaction
    ).filter_by(
        supplier_id=supplier_id
    ).order_by(
        WalletTransaction.created_at.desc()
    ).limit(100).all()

    result = []

    for tx in txs:

        result.append({

            "id":
                str(tx.id),

            "amount":
                tx.amount,

            "type":
                tx.type,

            "status":
                tx.status,

            "authority":
                tx.authority,

            "created_at":
                str(tx.created_at)
        })

    return {

        "success": True,

        "transactions":
            result
    }
