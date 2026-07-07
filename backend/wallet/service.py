# wallet/service.py

from datetime import datetime
from sqlalchemy.orm import Session

import models

from wallet.ledger import (
    create_credit_tx,
    create_wallet_tx,
)


# =========================================================
# GET SUPPLIER
# =========================================================

def get_supplier(
    db: Session,
    supplier_id,
):
    return (
        db.query(models.Supplier)
        .filter_by(id=supplier_id)
        .first()
    )


# =========================================================
# CREDIT BALANCE
# =========================================================

def get_credit_balance(
    db: Session,
    supplier_id,
):
    supplier = get_supplier(
        db,
        supplier_id,
    )

    if not supplier:
        return 0

    return supplier.credit_balance or 0


# =========================================================
# WALLET BALANCE
# =========================================================

def get_wallet_balance(
    db: Session,
    supplier_id,
):
    supplier = get_supplier(
        db,
        supplier_id,
    )

    if not supplier:
        return 0

    return supplier.wallet_balance or 0


# =========================================================
# ADD CREDIT
# =========================================================

def add_credit(
    db: Session,
    supplier_id,
    amount,
    tx_type="credit_purchase",
    reference_id=None,
    description=None,
):
    supplier = get_supplier(
        db,
        supplier_id,
    )

    if not supplier:
        return False

    amount = int(amount)

    supplier.credit_balance = (
        supplier.credit_balance or 0
    ) + amount

    create_credit_tx(
        db=db,
        supplier_id=supplier.id,
        amount=amount,
        tx_type=tx_type,
        reference_id=reference_id,
        balance_after=supplier.credit_balance,
        description=description,
    )

    db.commit()

    return True


# =========================================================
# DEDUCT CREDIT
# =========================================================

def deduct_credit(
    db: Session,
    supplier_id,
    amount,
    tx_type="credit_usage",
    reference_id=None,
    description=None,
):
    supplier = get_supplier(
        db,
        supplier_id,
    )

    if not supplier:
        return False

    amount = int(amount)

    balance = (
        supplier.credit_balance or 0
    )

    if balance < amount:
        return False

    supplier.credit_balance = (
        balance - amount
    )

    create_credit_tx(
        db=db,
        supplier_id=supplier.id,
        amount=-amount,
        tx_type=tx_type,
        reference_id=reference_id,
        balance_after=supplier.credit_balance,
        description=description,
    )

    db.commit()

    return True


# =========================================================
# ADD WALLET BALANCE
# =========================================================

def add_wallet_balance(
    db: Session,
    supplier_id,
    amount,
    tx_type="wallet_charge",
    authority=None,
    reference_id=None,
    description=None,
):
    supplier = get_supplier(
        db,
        supplier_id,
    )

    if not supplier:
        return False

    amount = int(amount)

    supplier.wallet_balance = (
        supplier.wallet_balance or 0
    ) + amount

    create_wallet_tx(
        db=db,
        supplier_id=supplier.id,
        amount=amount,
        tx_type=tx_type,
        authority=authority,
        status="success",
        reference_id=reference_id,
        balance_after=supplier.wallet_balance,
        description=description,
    )

    db.commit()

    return True


# =========================================================
# DEDUCT WALLET BALANCE
# =========================================================

def deduct_wallet_balance(
    db: Session,
    supplier_id,
    amount,
    tx_type="wallet_usage",
    authority=None,
    reference_id=None,
    description=None,
):
    supplier = get_supplier(
        db,
        supplier_id,
    )

    if not supplier:
        return False

    amount = int(amount)

    balance = (
        supplier.wallet_balance or 0
    )

    if balance < amount:
        return False

    supplier.wallet_balance = (
        balance - amount
    )

    create_wallet_tx(
        db=db,
        supplier_id=supplier.id,
        amount=-amount,
        tx_type=tx_type,
        authority=authority,
        status="success",
        reference_id=reference_id,
        balance_after=supplier.wallet_balance,
        description=description,
    )

    db.commit()

    return True


# =========================================================
# MONTHLY CREDIT GRANT
# =========================================================

def grant_monthly_credit(
    db: Session,
    supplier_id,
    amount,
):
    return add_credit(
        db=db,
        supplier_id=supplier_id,
        amount=amount,
        tx_type="monthly_grant",
        reference_id=datetime.utcnow().strftime(
            "%Y-%m"
        ),
        description="monthly free credits",
    )


# =========================================================
# WALLET TO CREDIT
# =========================================================

def convert_wallet_to_credit(
    db: Session,
    supplier_id,
    wallet_amount,
    credit_amount,
):
    ok = deduct_wallet_balance(
        db=db,
        supplier_id=supplier_id,
        amount=wallet_amount,
        tx_type="wallet_to_credit",
        description="wallet converted to credit",
    )

    if not ok:
        return False

    add_credit(
        db=db,
        supplier_id=supplier_id,
        amount=credit_amount,
        tx_type="wallet_conversion",
        description="credit purchased from wallet",
    )

    return True


# =========================================================
# BALANCE SUMMARY
# =========================================================

def get_balance_summary(
    db: Session,
    supplier_id,
):
    supplier = get_supplier(
        db,
        supplier_id,
    )

    if not supplier:
        return None

    return {
        "supplier_id": str(supplier.id),
        "credit_balance": supplier.credit_balance or 0,
        "wallet_balance": supplier.wallet_balance or 0,
        "wins": supplier.wins or 0,
        "score": supplier.score or 0,
    }
