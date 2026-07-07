from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from database import get_db

from scoring.service import (

    add_review,

    calculate_supplier_reputation,

    sync_supplier_metrics
)


router = APIRouter(

    prefix="/scoring",

    tags=["scoring"]
)


# =========================================================
# ADD REVIEW
# =========================================================

@router.post("/review")
def review(

    payload: dict,

    db: Session = Depends(get_db)
):

    supplier_id = payload.get(
        "supplier_id"
    )

    rating = payload.get(
        "rating"
    )

    review_text = payload.get(
        "review"
    )

    client_id = payload.get(
        "client_id"
    )

    lead_id = payload.get(
        "lead_id"
    )

    if not supplier_id:

        return {

            "success": False,

            "error": "supplier_required"
        }

    if rating is None:

        return {

            "success": False,

            "error": "rating_required"
        }

    ok = add_review(

        db=db,

        supplier_id=supplier_id,

        rating=rating,

        review=review_text,

        client_id=client_id,

        lead_id=lead_id
    )

    return {

        "success": ok
    }


# =========================================================
# REPUTATION
# =========================================================

@router.get("/supplier/{supplier_id}")
def reputation(

    supplier_id: str,

    db: Session = Depends(get_db)
):

    sync_supplier_metrics(
        db,
        supplier_id
    )

    result = calculate_supplier_reputation(
        db,
        supplier_id
    )

    return {

        "success": True,

        "data": result
    }