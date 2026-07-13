# admin/dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import (
    Client,
    CreditTransaction,
    Lead,
    LeadMatch,
    PaymentTransaction,
    Supplier,
    WalletTransaction,
)

router = APIRouter(prefix="/admin/dashboard", tags=["admin-dashboard"])


@router.get("")
def dashboard(db: Session = Depends(get_db)):
    total_suppliers = db.query(Supplier).count()

    total_clients = db.query(Client).count()

    total_leads = db.query(Lead).count()

    open_leads = db.query(Lead).filter(Lead.status == "open").count()

    claimed_leads = db.query(Lead).filter(Lead.status == "claimed").count()

    closed_leads = db.query(Lead).filter(Lead.status == "closed").count()

    total_matches = db.query(LeadMatch).count()

    total_payments = (
        db.query(
            func.coalesce(func.sum(PaymentTransaction.amount), 0)
        )
        .filter(PaymentTransaction.status == "paid")
        .scalar()
    )

    wallet_volume = (
        db.query(
            func.coalesce(func.sum(WalletTransaction.amount), 0)
        ).scalar()
    )

    credit_volume = (
        db.query(
            func.coalesce(func.sum(CreditTransaction.amount), 0)
        ).scalar()
    )

    return {
        "success": True,
        "suppliers": total_suppliers,
        "clients": total_clients,
        "leads": {
            "total": total_leads,
            "open": open_leads,
            "claimed": claimed_leads,
            "closed": closed_leads,
        },
        "matches": total_matches,
        "payments_total": total_payments,
        "wallet_volume": wallet_volume,
        "credit_volume": credit_volume,
    }