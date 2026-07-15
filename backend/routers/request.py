from datetime import datetime

from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from database import get_db

import models

from services.lead_bus import (
    process_new_lead
)


router = APIRouter(
    prefix="/request",
    tags=["request"]
)


# =========================================================
# CREATE REQUEST
# =========================================================

@router.post("")
async def create_request(
    payload: dict,
    db: Session = Depends(get_db),
):
    required = [
        "category_id",
        "subcategory_id",
        "location_id",
        "problem",
        "phone",
    ]

    for field in required:
        if not payload.get(field):
            return {
                "success": False,
                "error": f"missing_{field}",
            }

    client = (
        db.query(models.Client)
        .filter_by(phone=payload["phone"])
        .first()
    )

    if not client:
        client = models.Client(
            full_name=payload.get(
                "full_name",
                "کاربر",
            ),
            phone=payload["phone"],
        )

        db.add(client)
        db.commit()
        db.refresh(client)

    lead = models.Lead(
        client_id=client.id,
        category_id=payload["category_id"],
        subcategory_id=payload["subcategory_id"],
        location_id=payload["location_id"],
        problem=payload["problem"],
        priority_mode=payload.get(
            "priority_mode",
            "smart",
        ),
        status="open",
        created_at=datetime.utcnow(),
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    result = await process_new_lead(
        db,
        lead.id,
    )

    return {
        "success": True,
        "lead_id": str(lead.id),
        "matches": result.get(
            "matches",
            0,
        ),
        "notifications": result.get(
            "notifications",
            0,
        ),
    }

# =========================================================
# LEAD STATUS
# =========================================================

@router.get("/{lead_id}")
def lead_status(
    lead_id: str,
    db: Session = Depends(get_db)
):

    lead = db.query(
        models.Lead
    ).filter_by(
        id=lead_id
    ).first()

    if not lead:

        return {

            "success": False,

            "error":
                "lead_not_found"
        }

    return {

        "success": True,

        "lead": {

            "id":
                str(lead.id),

            "status":
                lead.status,

            "priority_mode":
                lead.priority_mode,

            "created_at":
                lead.created_at
        }
    }