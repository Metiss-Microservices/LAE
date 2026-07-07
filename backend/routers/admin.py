from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from database import get_db

from models import (
    Supplier,
    Lead,
    Client,
    LeadMatch
)

router = APIRouter(
    prefix="/admin"
)


# =========================================================
# dashboard
# =========================================================

@router.get("/stats")
def stats(
    db: Session = Depends(get_db)
):

    suppliers = db.query(Supplier).count()

    leads = db.query(Lead).count()

    clients = db.query(Client).count()

    matches = db.query(LeadMatch).count()

    return {

        "success": True,

        "stats": {

            "suppliers":
                suppliers,

            "clients":
                clients,

            "leads":
                leads,

            "matches":
                matches
        }
    }


# =========================================================
# latest leads
# =========================================================

@router.get("/latest-leads")
def latest_leads(
    db: Session = Depends(get_db)
):

    rows = db.query(
        Lead
    ).order_by(
        Lead.created_at.desc()
    ).limit(50).all()

    result = []

    for row in rows:

        result.append({

            "id":
                str(row.id),

            "problem":
                row.problem,

            "created_at":
                str(row.created_at)
        })

    return {

        "success": True,

        "leads":
            result
    }
