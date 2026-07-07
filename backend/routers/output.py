from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from database import get_db

from services.output_service import (
    build_output
)


router = APIRouter(
    prefix="/output",
    tags=["output"]
)


# =========================================================
# LEAD OUTPUT
# =========================================================

@router.get("/{lead_id}")
def get_output(
    lead_id: str,
    db: Session = Depends(get_db)
):

    return build_output(

        db=db,

        lead_id=lead_id
    )


# =========================================================
# SIMPLE SUMMARY
# =========================================================

@router.get("/{lead_id}/summary")
def get_summary(
    lead_id: str,
    db: Session = Depends(get_db)
):

    result = build_output(

        db=db,

        lead_id=lead_id
    )

    if not result.get(
        "success"
    ):
        return result

    return {

        "success": True,

        "lead_id":
            result["lead"]["id"],

        "status":
            result["lead"]["status"],

        "priority_mode":
            result["lead"]["priority_mode"],

        "supplier_count":
            result["supplier_count"],

        "winner":
            result["winner"]
    }