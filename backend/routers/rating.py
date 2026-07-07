from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from datetime import datetime

from database import get_db

from models import (
    SupplierReview,
    Supplier,
    Lead
)

router = APIRouter(
    prefix="/rating"
)


# =========================================================
# submit review
# =========================================================

@router.post("/submit")
def submit_review(
    payload: dict,
    db: Session = Depends(get_db)
):

    supplier_id = payload.get(
        "supplier_id"
    )

    lead_id = payload.get(
        "lead_id"
    )

    rating = payload.get(
        "rating"
    )

    review = payload.get(
        "review",
        ""
    )

    if (
        not supplier_id
        or
        not lead_id
        or
        rating is None
    ):

        return {
            "success": False,
            "error": "invalid_input"
        }

    supplier = db.query(Supplier).filter_by(
        id=supplier_id
    ).first()

    if not supplier:

        return {
            "success": False,
            "error": "supplier_not_found"
        }

    lead = db.query(Lead).filter_by(
        id=lead_id
    ).first()

    if not lead:

        return {
            "success": False,
            "error": "lead_not_found"
        }

    row = SupplierReview(

        supplier_id=supplier_id,

        lead_id=lead_id,

        rating=rating,

        review=review,

        created_at=datetime.utcnow()
    )

    db.add(row)

    db.commit()

    return {
        "success": True
    }


# =========================================================
# get supplier reviews
# =========================================================

@router.get("/{supplier_id}")
def get_reviews(
    supplier_id: str,
    db: Session = Depends(get_db)
):

    rows = db.query(
        SupplierReview
    ).filter_by(
        supplier_id=supplier_id
    ).order_by(
        SupplierReview.created_at.desc()
    ).all()

    result = []

    for r in rows:

        result.append({

            "id":
                str(r.id),

            "rating":
                r.rating,

            "review":
                r.review,

            "created_at":
                str(r.created_at)
        })

    return {

        "success": True,

        "reviews":
            result
    }
