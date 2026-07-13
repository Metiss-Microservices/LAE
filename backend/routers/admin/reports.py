from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from admin.reports import (
    build_executive_report,
    lead_report,
    supplier_report,
)
from database import get_db
from identity.dependencies import admin_required

router = APIRouter(prefix="/admin/reports", tags=["admin-reports"])


# =========================================================
# EXECUTIVE
# =========================================================

@router.get("/executive")
def executive_report(
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    return {
        "success": True,
        "report": build_executive_report(db),
    }


# =========================================================
# SUPPLIER
# =========================================================

@router.get("/supplier/{supplier_id}")
def supplier_details(
    supplier_id: str,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    return {
        "success": True,
        "report": supplier_report(db, supplier_id),
    }


# =========================================================
# LEAD
# =========================================================

@router.get("/lead/{lead_id}")
def lead_details(
    lead_id: str,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    return {
        "success": True,
        "report": lead_report(db, lead_id),
    }