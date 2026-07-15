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
    Client,
    Category,
    SubCategory,
    Location,
    Supplier,
)


router = APIRouter(
    prefix="/admin/leads",
    tags=["admin-leads"],
)


# =========================================================
# SERIALIZER HELPERS
# =========================================================

def serialize_datetime(value):
    return (
        value.isoformat()
        if value
        else None
    )


def get_optional_attr(
    obj,
    field_name,
    default=None,
):
    return getattr(
        obj,
        field_name,
        default,
    )


# =========================================================
# LIST LEADS
# =========================================================

@router.get("")
def list_leads(
    status: str | None = Query(None),
    category_id: str | None = Query(None),
    priority_mode: str | None = Query(None),
    limit: int = Query(
        100,
        ge=1,
        le=500,
    ),
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    query = db.query(Lead)

    if status:
        query = query.filter(
            Lead.status == status
        )

    if category_id:
        query = query.filter(
            Lead.category_id == category_id
        )

    if priority_mode:
        query = query.filter(
            Lead.priority_mode == priority_mode
        )

    rows = (
        query
        .order_by(
            Lead.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    result = []

    for lead in rows:
        match_count = (
            db.query(LeadMatch)
            .filter(
                LeadMatch.lead_id == lead.id
            )
            .count()
        )

        won_match = (
            db.query(LeadMatch)
            .filter(
                LeadMatch.lead_id == lead.id,
                LeadMatch.status == "won",
            )
            .first()
        )

        result.append({
            "id": str(lead.id),

            "client_id": (
                str(lead.client_id)
                if lead.client_id
                else None
            ),

            "status": lead.status,

            "priority_mode": (
                lead.priority_mode
            ),

            "category_id": (
                str(lead.category_id)
                if lead.category_id
                else None
            ),

            "subcategory_id": (
                str(lead.subcategory_id)
                if lead.subcategory_id
                else None
            ),

            "location_id": (
                str(lead.location_id)
                if lead.location_id
                else None
            ),

            "winner_supplier_id": (
                str(lead.winner_supplier_id)
                if lead.winner_supplier_id
                else None
            ),

            "winner_match_id": (
                str(won_match.id)
                if won_match
                else None
            ),

            "problem": lead.problem,

            "match_count": match_count,

            "created_at": serialize_datetime(
                lead.created_at
            ),

            "closed_at": serialize_datetime(
                get_optional_attr(
                    lead,
                    "closed_at",
                )
            ),

            "race_started_at": serialize_datetime(
                get_optional_attr(
                    lead,
                    "race_started_at",
                )
            ),

            "race_expires_at": serialize_datetime(
                get_optional_attr(
                    lead,
                    "race_expires_at",
                )
            ),
        })

    return {
        "success": True,
        "count": len(result),
        "items": result,
    }


# =========================================================
# LEAD DETAILS
# =========================================================

@router.get("/{lead_id}")
def lead_details(
    lead_id: str,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    lead = (
        db.query(Lead)
        .filter(
            Lead.id == lead_id
        )
        .first()
    )

    if not lead:
        return {
            "success": False,
            "error": "lead_not_found",
        }

    client = (
        db.query(Client)
        .filter(
            Client.id == lead.client_id
        )
        .first()
    )

    category = (
        db.query(Category)
        .filter(
            Category.id == lead.category_id
        )
        .first()
    )

    subcategory = (
        db.query(SubCategory)
        .filter(
            SubCategory.id
            == lead.subcategory_id
        )
        .first()
    )

    location = (
        db.query(Location)
        .filter(
            Location.id == lead.location_id
        )
        .first()
    )

    matches = (
        db.query(LeadMatch)
        .filter(
            LeadMatch.lead_id == lead.id
        )
        .order_by(
            LeadMatch.final_score.desc()
        )
        .all()
    )

    match_items = []

    for match in matches:
        supplier = (
            db.query(Supplier)
            .filter(
                Supplier.id
                == match.supplier_id
            )
            .first()
        )

        match_items.append({
            "id": str(match.id),

            "supplier_id": (
                str(match.supplier_id)
                if match.supplier_id
                else None
            ),

            "supplier_name": (
                supplier.full_name
                if supplier
                else None
            ),

            "status": match.status,

            "final_score": (
                float(match.final_score or 0)
            ),

            "base_score": (
                float(match.base_score or 0)
            ),

            "bid_price": (
                float(match.bid_price or 0)
            ),

            "created_at": serialize_datetime(
                match.created_at
            ),

            "expires_at": serialize_datetime(
                match.expires_at
            ),

            "won_at": serialize_datetime(
                match.won_at
            ),
        })

    return {
        "success": True,

        "lead": {
            "id": str(lead.id),

            "status": lead.status,

            "problem": lead.problem,

            "priority_mode": (
                lead.priority_mode
            ),

            "winner_supplier_id": (
                str(lead.winner_supplier_id)
                if lead.winner_supplier_id
                else None
            ),

            "created_at": serialize_datetime(
                lead.created_at
            ),

            "closed_at": serialize_datetime(
                get_optional_attr(
                    lead,
                    "closed_at",
                )
            ),

            "race_started_at": serialize_datetime(
                get_optional_attr(
                    lead,
                    "race_started_at",
                )
            ),

            "race_expires_at": serialize_datetime(
                get_optional_attr(
                    lead,
                    "race_expires_at",
                )
            ),
        },

        "client": {
            "id": (
                str(client.id)
                if client
                else None
            ),

            "name": (
                client.full_name
                if client
                else None
            ),

            "phone": (
                client.phone
                if client
                else None
            ),
        },

        "category": (
            category.name
            if category
            else None
        ),

        "subcategory": (
            subcategory.name
            if subcategory
            else None
        ),

        "location": (
            location.name
            if location
            else None
        ),

        "match_count": len(matches),

        "matches": match_items,
    }