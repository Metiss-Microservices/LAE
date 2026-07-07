from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query

from sqlalchemy.orm import Session

from database import get_db

from identity.dependencies import (
    admin_required
)

from models import (
    Lead,
    LeadMatch,
    Client,
    Category,
    SubCategory,
    Location
)

router = APIRouter(
    prefix="/admin/leads",
    tags=["admin-leads"]
)


# =========================================================
# LIST LEADS
# =========================================================

@router.get("")
def list_leads(
    status: str | None = Query(None),
    category_id: str | None = Query(None),
    priority_mode: str | None = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    q = db.query(Lead)

    if status:
        q = q.filter(
            Lead.status == status
        )

    if category_id:
        q = q.filter(
            Lead.category_id == category_id
        )

    if priority_mode:
        q = q.filter(
            Lead.priority_mode == priority_mode
        )

    rows = q.order_by(
        Lead.created_at.desc()
    ).limit(limit).all()

    result = []

    for lead in rows:

        match_count = db.query(
            LeadMatch
        ).filter(
            LeadMatch.lead_id == lead.id
        ).count()

        result.append({

            "id":
                str(lead.id),

            "status":
                lead.status,

            "priority_mode":
                lead.priority_mode,

            "category_id":
                str(lead.category_id)
                if lead.category_id
                else None,

            "subcategory_id":
                str(lead.subcategory_id)
                if lead.subcategory_id
                else None,

            "location_id":
                str(lead.location_id)
                if lead.location_id
                else None,

            "problem":
                lead.problem,

            "budget":
                lead.budget,

            "race_started":
                lead.race_started_at,

            "race_expires":
                lead.race_expires_at,

            "match_count":
                match_count,

            "created_at":
                lead.created_at
        })

    return {

        "success": True,

        "count":
            len(result),

        "items":
            result
    }


# =========================================================
# LEAD DETAILS
# =========================================================

@router.get("/{lead_id}")
def lead_details(
    lead_id: str,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    lead = db.query(
        Lead
    ).filter(
        Lead.id == lead_id
    ).first()

    if not lead:

        return {

            "success": False,

            "error":
                "lead_not_found"
        }

    client = db.query(
        Client
    ).filter(
        Client.id == lead.client_id
    ).first()

    category = db.query(
        Category
    ).filter(
        Category.id == lead.category_id
    ).first()

    subcategory = db.query(
        SubCategory
    ).filter(
        SubCategory.id == lead.subcategory_id
    ).first()

    location = db.query(
        Location
    ).filter(
        Location.id == lead.location_id
    ).first()

    matches = db.query(
        LeadMatch
    ).filter(
        LeadMatch.lead_id == lead.id
    ).all()

    return {

        "success": True,

        "lead": {

            "id":
                str(lead.id),

            "status":
                lead.status,

            "problem":
                lead.problem,

            "budget":
                lead.budget,

            "priority_mode":
                lead.priority_mode,

            "created_at":
                lead.created_at,

            "race_started_at":
                lead.race_started_at,

            "race_expires_at":
                lead.race_expires_at
        },

        "client": {

            "id":
                str(client.id)
                if client else None,

            "name":
                getattr(
                    client,
                    "full_name",
                    None
                ),

            "phone":
                getattr(
                    client,
                    "phone",
                    None
                )
        },

        "category":
            category.name
            if category
            else None,

        "subcategory":
            subcategory.name
            if subcategory
            else None,

        "location":
            location.name
            if location
            else None,

        "matches":
            len(matches)
    }


# =========================================================
# FORCE CLOSE
# =========================================================

@router.post("/{lead_id}/close")
def close_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    lead = db.query(
        Lead
    ).filter(
        Lead.id == lead_id
    ).first()

    if not lead:

        return {

            "success": False,

            "error":
                "lead_not_found"
        }

    lead.status = "closed"

    db.commit()

    return {

        "success": True,

        "lead_id":
            str(lead.id),

        "status":
            lead.status
    }


# =========================================================
# REOPEN
# =========================================================

@router.post("/{lead_id}/reopen")
def reopen_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    lead = db.query(
        Lead
    ).filter(
        Lead.id == lead_id
    ).first()

    if not lead:

        return {

            "success": False,

            "error":
                "lead_not_found"
        }

    lead.status = "open"

    db.commit()

    return {

        "success": True,

        "lead_id":
            str(lead.id),

        "status":
            lead.status
    }


# =========================================================
# STUCK RACES
# =========================================================

@router.get("/health/stuck-races")
def stuck_races(
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    now = datetime.utcnow()

    rows = db.query(
        Lead
    ).filter(
        Lead.status == "race",
        Lead.race_expires_at < now
    ).all()

    return {

        "success": True,

        "count":
            len(rows),

        "items": [

            {
                "lead_id":
                    str(x.id),

                "expired_at":
                    x.race_expires_at
            }

            for x in rows
        ]
    }
