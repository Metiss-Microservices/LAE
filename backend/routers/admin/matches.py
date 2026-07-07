from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query

from sqlalchemy.orm import Session

from database import get_db

from identity.dependencies import (
    admin_required
)

from models import (
    LeadMatch,
    Supplier,
    Lead
)

router = APIRouter(
    prefix="/admin/matches",
    tags=["admin-matches"]
)


@router.get("")
def list_matches(
    lead_id: str | None = Query(None),
    supplier_id: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(200, le=1000),
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    q = db.query(LeadMatch)

    if lead_id:
        q = q.filter(
            LeadMatch.lead_id == lead_id
        )

    if supplier_id:
        q = q.filter(
            LeadMatch.supplier_id == supplier_id
        )

    if status:
        q = q.filter(
            LeadMatch.status == status
        )

    rows = (
        q.order_by(
            LeadMatch.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    result = []

    for row in rows:

        result.append({

            "id":
                str(row.id),

            "lead_id":
                str(row.lead_id),

            "supplier_id":
                str(row.supplier_id),

            "score":
                row.score,

            "status":
                row.status,

            "auction_price":
                getattr(
                    row,
                    "auction_price",
                    None
                ),

            "created_at":
                row.created_at
        })

    return {

        "success": True,

        "count":
            len(result),

        "items":
            result
    }


@router.get("/{match_id}")
def match_details(
    match_id: str,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    row = db.query(
        LeadMatch
    ).filter(
        LeadMatch.id == match_id
    ).first()

    if not row:

        return {
            "success": False,
            "error": "match_not_found"
        }

    supplier = db.query(
        Supplier
    ).filter(
        Supplier.id == row.supplier_id
    ).first()

    lead = db.query(
        Lead
    ).filter(
        Lead.id == row.lead_id
    ).first()

    return {

        "success": True,

        "match": {

            "id":
                str(row.id),

            "lead_id":
                str(row.lead_id),

            "supplier_id":
                str(row.supplier_id),

            "supplier_name":
                supplier.full_name
                if supplier
                else None,

            "score":
                row.score,

            "status":
                row.status,

            "auction_price":
                getattr(
                    row,
                    "auction_price",
                    None
                ),

            "lead_status":
                lead.status
                if lead
                else None
        }
    }


@router.get("/reports/winners")
def winner_report(
    limit: int = 100,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    rows = db.query(
        LeadMatch
    ).filter(
        LeadMatch.status == "won"
    ).order_by(
        LeadMatch.created_at.desc()
    ).limit(limit).all()

    return {

        "success": True,

        "items": [

            {

                "match_id":
                    str(x.id),

                "lead_id":
                    str(x.lead_id),

                "supplier_id":
                    str(x.supplier_id),

                "score":
                    x.score
            }

            for x in rows
        ]
    }
