from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from datetime import datetime

from database import get_db

from models import (
    Request,
    Lead
)

router = APIRouter(
    prefix="/lead"
)


# =========================================================
# create manual lead
# =========================================================

@router.post("/manual")
def create_lead_manual(
    request_id: str,
    db: Session = Depends(get_db)
):

    """
    ⚠️ INTERNAL ONLY
    debug / migration / testing
    """

    req = db.query(Request).filter(
        Request.id == request_id
    ).first()

    if not req:

        return {
            "success": False,
            "error": "request_not_found"
        }

    existing = db.query(Lead).filter(
        Lead.request_id == request_id
    ).first()

    if existing:

        return {

            "success": True,

            "lead_id":
                str(existing.id),

            "message":
                "already_exists"
        }

    lead = Lead(

        request_id=req.id,

        category_id=req.category_id,

        subcategory_id=req.subcategory_id,

        location_id=req.location_id,

        client_id=req.client_id,

        problem=req.problem,

        created_at=datetime.utcnow()
    )

    db.add(lead)

    db.commit()

    db.refresh(lead)

    return {

        "success": True,

        "lead_id":
            str(lead.id)
    }