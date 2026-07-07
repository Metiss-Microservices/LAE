# services/lead_bus.py

from sqlalchemy.orm import Session

import models

from services.matching_service import (
    match_lead
)

from services.notification_dispatcher import (
    dispatch_new_lead
)


# =========================================================
# CREATE EVENT
# =========================================================

def create_event(

    db: Session,

    lead_id,

    event_type,

    supplier_id=None,

    payload=None
):

    event = models.LeadEvent(

        lead_id=lead_id,

        supplier_id=supplier_id,

        event_type=event_type,

        payload=payload
    )

    db.add(event)

    db.commit()

    db.refresh(event)

    return event


# =========================================================
# PROCESS NEW LEAD
# =========================================================

async def process_new_lead(

    db: Session,

    lead_id
):

    lead = db.query(
        models.Lead
    ).filter_by(
        id=lead_id
    ).first()

    if not lead:

        return {

            "success": False,

            "error": "lead_not_found"
        }

    create_event(

        db,

        lead.id,

        "lead_created"
    )

    matches = match_lead(

        db,

        lead.id
    )

    create_event(

        db,

        lead.id,

        "matching_completed",

        payload=str(
            len(matches)
        )
    )

    dispatch_result = await dispatch_new_lead(

        db,

        lead.id
    )

    create_event(

        db,

        lead.id,

        "notifications_sent",

        payload=str(
            dispatch_result.get(
                "sent_count",
                0
            )
        )
    )

    return {

        "success": True,

        "lead_id":
            str(lead.id),

        "matches":
            len(matches),

        "notifications":
            dispatch_result.get(
                "sent_count",
                0
            )
    }


# =========================================================
# REPROCESS LEAD
# =========================================================

async def reprocess_lead(

    db: Session,

    lead_id
):

    db.query(
        models.LeadMatch
    ).filter_by(
        lead_id=lead_id
    ).delete()

    db.commit()

    create_event(

        db,

        lead_id,

        "lead_reprocessed"
    )

    return await process_new_lead(

        db,

        lead_id
    )


# =========================================================
# GET EVENTS
# =========================================================

def get_lead_events(

    db: Session,

    lead_id
):

    return db.query(
        models.LeadEvent
    ).filter_by(

        lead_id=lead_id

    ).order_by(

        models.LeadEvent.created_at.desc()

    ).all()


# =========================================================
# GET EVENTS SERIALIZED
# =========================================================

def get_lead_events_json(

    db: Session,

    lead_id
):

    rows = get_lead_events(

        db,

        lead_id
    )

    result = []

    for row in rows:

        result.append({

            "id":
                str(row.id),

            "lead_id":
                str(row.lead_id),

            "supplier_id":
                str(row.supplier_id)
                if row.supplier_id
                else None,

            "event_type":
                row.event_type,

            "payload":
                row.payload,

            "created_at":
                row.created_at
        })

    return result


# =========================================================
# SUPPLIER EVENTS
# =========================================================

def get_supplier_events(

    db: Session,

    supplier_id,

    limit=100
):

    rows = db.query(
        models.LeadEvent
    ).filter_by(

        supplier_id=supplier_id

    ).order_by(

        models.LeadEvent.created_at.desc()

    ).limit(
        limit
    ).all()

    result = []

    for row in rows:

        result.append({

            "id":
                str(row.id),

            "lead_id":
                str(row.lead_id),

            "event_type":
                row.event_type,

            "payload":
                row.payload,

            "created_at":
                row.created_at
        })

    return result


# =========================================================
# AUDIT EVENT
# =========================================================

def audit(

    db: Session,

    lead_id,

    event_type,

    supplier_id=None,

    payload=None
):

    return create_event(

        db=db,

        lead_id=lead_id,

        supplier_id=supplier_id,

        event_type=event_type,

        payload=payload
    )