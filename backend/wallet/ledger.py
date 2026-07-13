# wallet/ledger.py

from datetime import datetime

from sqlalchemy.orm import Session

import models


# =========================================================
# CREDIT TRANSACTION
# =========================================================

def create_credit_tx(
    db: Session,
    supplier_id,
    amount,
    tx_type,
    reference_id=None,
    balance_after=None,
    description=None,
):
    tx = models.CreditTransaction(
        supplier_id=supplier_id,
        amount=amount,
        type=tx_type,
        reference_id=reference_id,
        balance_after=balance_after,
        description=description,
        created_at=datetime.utcnow(),
    )

    db.add(tx)

    return tx


# =========================================================
# WALLET TRANSACTION
# =========================================================

def create_wallet_tx(
    db: Session,
    supplier_id,
    amount,
    tx_type,
    authority=None,
    status="success",
    reference_id=None,
    balance_after=None,
    description=None,
):
    tx = models.WalletTransaction(
        supplier_id=supplier_id,
        amount=amount,
        type=tx_type,
        authority=authority,
        status=status,
        reference_id=reference_id,
        balance_after=balance_after,
        description=description,
        created_at=datetime.utcnow(),
    )

    db.add(tx)

    return tx


# =========================================================
# CREDIT HISTORY
# =========================================================

def get_credit_history(
    db: Session,
    supplier_id,
    limit=100,
):
    return (
        db.query(models.CreditTransaction)
        .filter_by(supplier_id=supplier_id)
        .order_by(models.CreditTransaction.created_at.desc())
        .limit(limit)
        .all()
    )


# =========================================================
# WALLET HISTORY
# =========================================================

def get_wallet_history(
    db: Session,
    supplier_id,
    limit=100,
):
    return (
        db.query(models.WalletTransaction)
        .filter_by(supplier_id=supplier_id)
        .order_by(models.WalletTransaction.created_at.desc())
        .limit(limit)
        .all()
    )


# =========================================================
# LAST CREDIT TX
# =========================================================

def get_last_credit_tx(
    db: Session,
    supplier_id,
):
    return (
        db.query(models.CreditTransaction)
        .filter_by(supplier_id=supplier_id)
        .order_by(models.CreditTransaction.created_at.desc())
        .first()
    )


# =========================================================
# LAST WALLET TX
# =========================================================

def get_last_wallet_tx(
    db: Session,
    supplier_id,
):
    return (
        db.query(models.WalletTransaction)
        .filter_by(supplier_id=supplier_id)
        .order_by(models.WalletTransaction.created_at.desc())
        .first()
    )

# =========================================================
# BACKWARD COMPATIBILITY
# =========================================================

def create_wallet_transaction(
    db,
    supplier_id,
    amount,
    tx_type,
    authority=None,
    status="success",
    reference_id=None,
    balance_after=None,
    description=None,
):
    return create_wallet_tx(
        db=db,
        supplier_id=supplier_id,
        amount=amount,
        tx_type=tx_type,
        authority=authority,
        status=status,
        reference_id=reference_id,
        balance_after=balance_after,
        description=description,
    )


def create_credit_transaction(
    db,
    supplier_id,
    amount,
    tx_type,
    reference_id=None,
    balance_after=None,
    description=None,
):
    return create_credit_tx(
        db=db,
        supplier_id=supplier_id,
        amount=amount,
        tx_type=tx_type,
        reference_id=reference_id,
        balance_after=balance_after,
        description=description,
    )

# =========================================================
# BACKWARD COMPATIBILITY
# =========================================================

def create_wallet_transaction(*args, **kwargs):
    return create_wallet_tx(*args, **kwargs)


def create_credit_transaction(*args, **kwargs):
    return create_credit_tx(*args, **kwargs)