from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from sqlalchemy.orm import Session

from database import get_db

from identity.dependencies import (
    admin_required,
)

from models import (
    Lead,
    LeadMatch,
    Supplier,
)


router = APIRouter(
    prefix="/admin/matches",
    tags=["admin-matches"],
)


# =========================================================
# HELPERS
# =========================================================

def serialize_datetime(value):
    return (
        value.isoformat()
        if value
        else None
    )


def serialize_match(
    row: LeadMatch,
    supplier: Supplier | None = None,
    lead: Lead | None = None,
):
    return {
        "id": str(row.id),

        "lead_id": (
            str(row.lead_id)
            if row.lead_id
            else None
        ),

        "supplier_id": (
            str(row.supplier_id)
            if row.supplier_id
            else None
        ),

        "supplier_name": (
            supplier.full_name
            if supplier
            else None
        ),

        "status": row.status,

        "final_score": float(
            row.final_score or 0
        ),

        "base_score": float(
            row.base_score or 0
        ),

        "bid_price": float(
            row.bid_price or 0
        ),

        "lead_status": (
            lead.status
            if lead
            else None
        ),

        "created_at": serialize_datetime(
            row.created_at
        ),

        "expires_at": serialize_datetime(
            row.expires_at
        ),

        "won_at": serialize_datetime(
            row.won_at
        ),
    }


# =========================================================
# WINNER REPORT
#
# Important:
# Static routes must be declared before /{match_id}.
# =========================================================

@router.get("/reports/winners")
def winner_report(
    limit: int = Query(
        100,
        ge=1,
        le=1000,
    ),
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    rows = (
        db.query(LeadMatch)
        .filter(
            LeadMatch.status == "won"
        )
        .order_by(
            LeadMatch.won_at.desc(),
            LeadMatch.created_at.desc(),
        )
        .limit(limit)
        .all()
    )

    result = []

    for row in rows:
        supplier = (
            db.query(Supplier)
            .filter(
                Supplier.id == row.supplier_id
            )
            .first()
        )

        lead = (
            db.query(Lead)
            .filter(
                Lead.id == row.lead_id
            )
            .first()
        )

        result.append(
            serialize_match(
                row=row,
                supplier=supplier,
                lead=lead,
            )
        )

    return {
        "success": True,
        "count": len(result),
        "items": result,
    }


# =========================================================
# LIST MATCHES
# =========================================================

@router.get("")
def list_matches(
    lead_id: str | None = Query(None),
    supplier_id: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(
        200,
        ge=1,
        le=1000,
    ),
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    query = db.query(LeadMatch)

    if lead_id:
        query = query.filter(
            LeadMatch.lead_id == lead_id
        )

    if supplier_id:
        query = query.filter(
            LeadMatch.supplier_id
            == supplier_id
        )

    if status:
        query = query.filter(
            LeadMatch.status == status
        )

    rows = (
        query
        .order_by(
            LeadMatch.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    result = []

    for row in rows:
        supplier = (
            db.query(Supplier)
            .filter(
                Supplier.id == row.supplier_id
            )
            .first()
        )

        lead = (
            db.query(Lead)
            .filter(
                Lead.id == row.lead_id
            )
            .first()
        )

        result.append(
            serialize_match(
                row=row,
                supplier=supplier,
                lead=lead,
            )
        )

    return {
        "success": True,
        "count": len(result),
        "items": result,
    }


# =========================================================
# MATCH DETAILS
#
# Dynamic route must remain after all static routes.
# =========================================================

@router.get("/{match_id}")
def match_details(
    match_id: str,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    row = (
        db.query(LeadMatch)
        .filter(
            LeadMatch.id == match_id
        )
        .first()
    )

    if not row:
        return {
            "success": False,
            "error": "match_not_found",
        }

    supplier = (
        db.query(Supplier)
        .filter(
            Supplier.id == row.supplier_id
        )
        .first()
    )

    lead = (
        db.query(Lead)
        .filter(
            Lead.id == row.lead_id
        )
        .first()
    )

    return {
        "success": True,
        "match": serialize_match(
            row=row,
            supplier=supplier,
            lead=lead,
        ),
    }