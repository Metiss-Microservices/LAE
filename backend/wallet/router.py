from fastapi import (
    APIRouter,
    Depends,
    Header
)

from sqlalchemy.orm import Session

from database import get_db

from models import (
    WalletTransaction,
    CreditTransaction
)

from wallet.service import (
    get_wallet_balance,
    get_credit_balance,
    wallet_to_credit,
    add_credit,
    deduct_credit
)

from identity.service import (
    get_supplier_by_token
)


router = APIRouter(
    prefix="/wallet",
    tags=["wallet"]
)


# =========================================================
# AUTH
# =========================================================

def auth_supplier(
    db,
    token
):

    if not token:
        return None

    return get_supplier_by_token(
        db,
        token
    )


# =========================================================
# BALANCE
# =========================================================

@router.get("/balance")
def balance(

    token: str = Header(None),

    db: Session = Depends(get_db)
):

    supplier = auth_supplier(
        db,
        token
    )

    if not supplier:

        return {

            "success": False,

            "error":
                "unauthorized"
        }

    return {

        "success": True,

        "wallet_balance":
            get_wallet_balance(
                db,
                supplier.id
            ),

        "credit_balance":
            get_credit_balance(
                db,
                supplier.id
            )
    }


# =========================================================
# WALLET TX
# =========================================================

@router.get("/transactions/wallet")
def wallet_transactions(

    token: str = Header(None),

    db: Session = Depends(get_db)
):

    supplier = auth_supplier(
        db,
        token
    )

    if not supplier:

        return {

            "success": False,

            "error":
                "unauthorized"
        }

    rows = db.query(
        WalletTransaction
    ).filter_by(

        supplier_id=supplier.id

    ).order_by(

        WalletTransaction.created_at.desc()

    ).limit(
        100
    ).all()

    result = []

    for row in rows:

        result.append({

            "id":
                str(row.id),

            "amount":
                row.amount,

            "type":
                row.type,

            "authority":
                row.authority,

            "status":
                row.status,

            "reference_id":
                row.reference_id,

            "description":
                row.description,

            "created_at":
                str(
                    row.created_at
                )
        })

    return {

        "success": True,

        "transactions":
            result
    }


# =========================================================
# CREDIT TX
# =========================================================

@router.get("/transactions/credit")
def credit_transactions(

    token: str = Header(None),

    db: Session = Depends(get_db)
):

    supplier = auth_supplier(
        db,
        token
    )

    if not supplier:

        return {

            "success": False,

            "error":
                "unauthorized"
        }

    rows = db.query(
        CreditTransaction
    ).filter_by(

        supplier_id=supplier.id

    ).order_by(

        CreditTransaction.created_at.desc()

    ).limit(
        100
    ).all()

    result = []

    for row in rows:

        result.append({

            "id":
                str(row.id),

            "amount":
                row.amount,

            "type":
                row.type,

            "reference_id":
                row.reference_id,

            "description":
                row.description,

            "created_at":
                str(
                    row.created_at
                )
        })

    return {

        "success": True,

        "transactions":
            result
    }


# =========================================================
# ALL TX
# =========================================================

@router.get("/transactions")
def all_transactions(

    token: str = Header(None),

    db: Session = Depends(get_db)
):

    supplier = auth_supplier(
        db,
        token
    )

    if not supplier:

        return {

            "success": False,

            "error":
                "unauthorized"
        }

    wallet_rows = db.query(
        WalletTransaction
    ).filter_by(

        supplier_id=supplier.id

    ).order_by(

        WalletTransaction.created_at.desc()

    ).limit(
        50
    ).all()

    credit_rows = db.query(
        CreditTransaction
    ).filter_by(

        supplier_id=supplier.id

    ).order_by(

        CreditTransaction.created_at.desc()

    ).limit(
        50
    ).all()

    wallet_result = []

    for row in wallet_rows:

        wallet_result.append({

            "id":
                str(row.id),

            "amount":
                row.amount,

            "type":
                row.type,

            "status":
                row.status,

            "reference_id":
                row.reference_id,

            "created_at":
                str(
                    row.created_at
                )
        })

    credit_result = []

    for row in credit_rows:

        credit_result.append({

            "id":
                str(row.id),

            "amount":
                row.amount,

            "type":
                row.type,

            "reference_id":
                row.reference_id,

            "created_at":
                str(
                    row.created_at
                )
        })

    return {

        "success": True,

        "wallet_transactions":
            wallet_result,

        "credit_transactions":
            credit_result
    }


# =========================================================
# CONVERT
# =========================================================

@router.post("/convert")
def convert_wallet(

    payload: dict,

    token: str = Header(None),

    db: Session = Depends(get_db)
):

    supplier = auth_supplier(
        db,
        token
    )

    if not supplier:

        return {

            "success": False,

            "error":
                "unauthorized"
        }

    toman_amount = int(

        payload.get(
            "toman_amount",
            0
        )
    )

    credit_amount = int(

        payload.get(
            "credit_amount",
            0
        )
    )

    if toman_amount <= 0:

        return {

            "success": False,

            "error":
                "invalid_amount"
        }

    ok = wallet_to_credit(

        db=db,

        supplier_id=
            supplier.id,

        toman_amount=
            toman_amount,

        credit_amount=
            credit_amount
    )

    return {

        "success": ok
    }


# =========================================================
# ADMIN CREDIT ADD
# =========================================================

@router.post("/admin/add-credit")
def admin_add_credit(

    payload: dict,

    db: Session = Depends(get_db)
):

    supplier_id = payload.get(
        "supplier_id"
    )

    amount = int(
        payload.get(
            "amount",
            0
        )
    )

    if amount <= 0:

        return {

            "success": False
        }

    return {

        "success":
            add_credit(

                db=db,

                supplier_id=
                    supplier_id,

                amount=
                    amount,

                tx_type=
                    "manual_credit",

                reference_id=
                    "admin"
            )
    }


# =========================================================
# ADMIN CREDIT REMOVE
# =========================================================

@router.post("/admin/remove-credit")
def admin_remove_credit(

    payload: dict,

    db: Session = Depends(get_db)
):

    supplier_id = payload.get(
        "supplier_id"
    )

    amount = int(
        payload.get(
            "amount",
            0
        )
    )

    if amount <= 0:

        return {

            "success": False
        }

    return {

        "success":
            deduct_credit(

                db=db,

                supplier_id=
                    supplier_id,

                amount=
                    amount,

                tx_type=
                    "manual_debit",

                reference_id=
                    "admin"
            )
    }