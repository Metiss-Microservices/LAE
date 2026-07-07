from fastapi import (
    APIRouter,
    Depends,
    Header
)

from sqlalchemy.orm import Session

from database import get_db

from rating.service import (
    create_review
)

from identity.service import (
    get_client_by_token
)

router = APIRouter(
    prefix="/rating",
    tags=["rating"]
)


@router.post("/supplier")
def rate_supplier(

    payload: dict,

    token: str = Header(None),

    db: Session = Depends(get_db)
):

    client = get_client_by_token(
        db,
        token
    )

    if not client:

        return {
            "success": False,
            "error": "unauthorized"
        }

    supplier_id = payload.get(
        "supplier_id"
    )

    lead_id = payload.get(
        "lead_id"
    )

    rating = payload.get(
        "rating"
    )

    comment = payload.get(
        "comment"
    )

    if not supplier_id:

        return {
            "success": False,
            "error": "missing_supplier"
        }

    if not lead_id:

        return {
            "success": False,
            "error": "missing_lead"
        }

    if rating is None:

        return {
            "success": False,
            "error": "missing_rating"
        }

    rating = float(rating)

    if rating < 1 or rating > 5:

        return {
            "success": False,
            "error": "invalid_rating"
        }

    return create_review(

        db=db,

        supplier_id=supplier_id,

        client_id=client.id,

        lead_id=lead_id,

        rating=rating,

        comment=comment
    )