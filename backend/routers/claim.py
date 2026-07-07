from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from database import get_db

from identity.dependencies import (
    get_current_supplier
)

from services.race_service import (
    claim_race_lead
)

from services.auction_service import (
    finalize_auction
)

import models


router = APIRouter(
    prefix="/claim",
    tags=["claim"]
)


# =========================================================
# CLAIM RACE LEAD
# =========================================================

@router.post("/race")
async def claim_race(
    payload: dict,
    supplier=Depends(
        get_current_supplier
    ),
    db: Session = Depends(get_db)
):

    match_id = payload.get(
        "match_id"
    )

    if not match_id:

        return {
            "success": False,
            "error":
                "missing_match_id"
        }

    return await claim_race_lead(

        db=db,

        supplier_id=
            supplier.id,

        match_id=
            match_id
    )


# =========================================================
# FINALIZE AUCTION
# =========================================================

@router.post("/auction/finalize")
def finalize_supplier_auction(
    payload: dict,
    supplier=Depends(
        get_current_supplier
    ),
    db: Session = Depends(get_db)
):

    lead_id = payload.get(
        "lead_id"
    )

    if not lead_id:

        return {
            "success": False,
            "error":
                "missing_lead_id"
        }

    match = db.query(
        models.LeadMatch
    ).filter(

        models.LeadMatch.lead_id
        == lead_id,

        models.LeadMatch.supplier_id
        == supplier.id

    ).first()

    if not match:

        return {
            "success": False,
            "error":
                "access_denied"
        }

    return finalize_auction(
        db,
        lead_id
    )


# =========================================================
# MY ACTIVE LEADS
# =========================================================

@router.get("/active")
def my_active_claims(
    supplier=Depends(
        get_current_supplier
    ),
    db: Session = Depends(get_db)
):

    matches = db.query(
        models.LeadMatch
    ).filter(

        models.LeadMatch.supplier_id
        == supplier.id,

        models.LeadMatch.status
        == "pending"

    ).all()

    return {

        "success": True,

        "count":
            len(matches),

        "items": [

            {
                "match_id":
                    str(m.id),

                "lead_id":
                    str(m.lead_id),

                "status":
                    m.status,

                "expires_at":
                    m.expires_at
            }

            for m in matches
        ]
    }