# payments/service.py

from datetime import datetime

from sqlalchemy.orm import Session

import models

from payments.providers.zarinpal import (
    create_payment as zarinpal_create_payment,
    verify_payment as zarinpal_verify_payment
)

from wallet.service import (
    add_wallet_balance
)

from wallet.ledger import (
    create_wallet_transaction
)


# =========================================================
# CREATE PAYMENT
# =========================================================

def create_payment(
    db: Session,
    supplier_id,
    amount,
    gateway="zarinpal"
):

    supplier = db.query(
        models.Supplier
    ).filter_by(
        id=supplier_id
    ).first()

    if not supplier:

        return {
            "success": False,
            "error": "supplier_not_found"
        }

    try:

        amount = int(amount)

    except Exception:

        return {
            "success": False,
            "error": "invalid_amount"
        }

    if amount <= 0:

        return {
            "success": False,
            "error": "invalid_amount"
        }

    callback_url = (
        "/payments/callback"
    )

    if gateway != "zarinpal":

        return {
            "success": False,
            "error": "unsupported_gateway"
        }

    gateway_result = zarinpal_create_payment(

        amount=amount,

        description="LAE Wallet Charge",

        callback_url=callback_url,

        phone=supplier.phone
    )

    if not gateway_result.get(
        "success"
    ):

        return {
            "success": False,
            "error": "gateway_error"
        }

    payment = models.PaymentTransaction(

        supplier_id=supplier.id,

        amount=amount,

        gateway=gateway,

        authority=(
            gateway_result.get(
                "authority"
            )
        ),

        status="pending",

        created_at=datetime.utcnow()
    )

    db.add(payment)

    db.commit()

    db.refresh(payment)

    return {

        "success": True,

        "payment_id":
            str(payment.id),

        "authority":
            payment.authority,

        "payment_url":
            gateway_result.get(
                "payment_url"
            )
    }


# =========================================================
# VERIFY PAYMENT
# =========================================================

def verify_payment(
    db: Session,
    authority
):

    payment = db.query(
        models.PaymentTransaction
    ).filter_by(
        authority=authority
    ).first()

    if not payment:

        return {
            "success": False,
            "error": "payment_not_found"
        }

    # -----------------------------------------
    # already verified
    # -----------------------------------------

    if payment.status == "paid":

        supplier = db.query(
            models.Supplier
        ).filter_by(
            id=payment.supplier_id
        ).first()

        return {

            "success": True,

            "already_verified": True,

            "wallet_balance":
                supplier.wallet_balance
                if supplier
                else 0
        }

    # -----------------------------------------
    # gateway verify
    # -----------------------------------------

    verify_result = (
        zarinpal_verify_payment(

            authority=authority,

            amount=payment.amount
        )
    )

    payment.verify_payload = str(
        verify_result
    )

    if not verify_result.get(
        "success"
    ):

        payment.status = "failed"

        payment.failure_reason = (
            "gateway_verify_failed"
        )

        db.commit()

        return {

            "success": False,

            "error":
                "verify_failed"
        }

    supplier = db.query(
        models.Supplier
    ).filter_by(
        id=payment.supplier_id
    ).first()

    if not supplier:

        payment.status = "failed"

        payment.failure_reason = (
            "supplier_not_found"
        )

        db.commit()

        return {

            "success": False,

            "error":
                "supplier_not_found"
        }

    # -----------------------------------------
    # wallet charge
    # -----------------------------------------

    add_wallet_balance(

        db=db,

        supplier_id=supplier.id,

        amount=payment.amount,

        tx_type="deposit",

        authority=payment.authority,

        reference_id=str(
            payment.id
        )
    )

    payment.status = "paid"

    payment.ref_id = (
        verify_result.get(
            "ref_id"
        )
    )

    payment.paid_at = (
        datetime.utcnow()
    )

    db.commit()

    db.refresh(supplier)

    return {

        "success": True,

        "payment_id":
            str(payment.id),

        "wallet_balance":
            supplier.wallet_balance,

        "ref_id":
            payment.ref_id
    }


# =========================================================
# FAIL PAYMENT
# =========================================================

def fail_payment(
    db: Session,
    payment_id,
    reason=None
):

    payment = db.query(
        models.PaymentTransaction
    ).filter_by(
        id=payment_id
    ).first()

    if not payment:

        return False

    payment.status = "failed"

    payment.failure_reason = reason

    db.commit()

    return True


# =========================================================
# GET PAYMENT
# =========================================================

def get_payment(
    db: Session,
    payment_id
):

    payment = db.query(
        models.PaymentTransaction
    ).filter_by(
        id=payment_id
    ).first()

    if not payment:

        return {

            "success": False,

            "error":
                "payment_not_found"
        }

    return {

        "success": True,

        "payment": {

            "id":
                str(payment.id),

            "supplier_id":
                str(
                    payment.supplier_id
                ),

            "amount":
                payment.amount,

            "gateway":
                payment.gateway,

            "authority":
                payment.authority,

            "ref_id":
                payment.ref_id,

            "status":
                payment.status,

            "failure_reason":
                payment.failure_reason,

            "created_at":
                payment.created_at,

            "paid_at":
                payment.paid_at
        }
    }


# =========================================================
# LIST PAYMENTS
# =========================================================

def get_supplier_payments(
    db: Session,
    supplier_id,
    limit=50
):

    rows = db.query(
        models.PaymentTransaction
    ).filter_by(
        supplier_id=supplier_id
    ).order_by(

        models.PaymentTransaction.created_at.desc()

    ).limit(
        limit
    ).all()

    result = []

    for row in rows:

        result.append({

            "id":
                str(row.id),

            "amount":
                row.amount,

            "gateway":
                row.gateway,

            "status":
                row.status,

            "authority":
                row.authority,

            "ref_id":
                row.ref_id,

            "failure_reason":
                row.failure_reason,

            "created_at":
                row.created_at,

            "paid_at":
                row.paid_at
        })

    return result


# =========================================================
# ADMIN LIST
# =========================================================

def get_recent_payments(
    db: Session,
    limit=100
):

    return db.query(
        models.PaymentTransaction
    ).order_by(

        models.PaymentTransaction.created_at.desc()

    ).limit(
        limit
    ).all()