# services/notification_dispatcher.py

from sqlalchemy.orm import Session

import models

from notifications.service import (
    notify_supplier,
    build_lead_message
)

from websocket.events import (
    emit_new_lead
)


# =========================================================
# LOCATION
# =========================================================

def get_location_name(
    db: Session,
    location_id
):

    loc = db.query(
        models.Location
    ).filter_by(
        id=location_id
    ).first()

    if not loc:
        return "-"

    names = []

    while loc:

        names.append(
            loc.name
        )

        if not loc.parent_id:
            break

        loc = db.query(
            models.Location
        ).filter_by(
            id=loc.parent_id
        ).first()

    names.reverse()

    return " / ".join(names)


# =========================================================
# BUILD PAYLOAD
# =========================================================

def build_ws_payload(
    lead,
    match
):

    return {

        "lead_id":
            str(lead.id),

        "match_id":
            str(match.id),

        "score":
            match.final_score,

        "priority_mode":
            lead.priority_mode,

        "problem":
            lead.problem,

        "status":
            lead.status
    }


# =========================================================
# DISPATCH SINGLE
# =========================================================

async def dispatch_single_supplier(
    db: Session,
    lead_id,
    supplier_id
):

    lead = db.query(
        models.Lead
    ).filter_by(
        id=lead_id
    ).first()

    if not lead:
        return False

    supplier = db.query(
        models.Supplier
    ).filter_by(
        id=supplier_id
    ).first()

    if not supplier:
        return False

    match = db.query(
        models.LeadMatch
    ).filter_by(

        lead_id=lead.id,

        supplier_id=supplier.id

    ).first()

    if not match:
        return False

    category = db.query(
        models.Category
    ).filter_by(
        id=lead.category_id
    ).first()

    subcategory = db.query(
        models.SubCategory
    ).filter_by(
        id=lead.subcategory_id
    ).first()

    message = build_lead_message(

        category.name
        if category
        else "-",

        subcategory.name
        if subcategory
        else "-",

        lead.problem,

        get_location_name(
            db,
            lead.location_id
        )
    )

    notify_supplier(
        supplier,
        message
    )

    await emit_new_lead(

        supplier.id,

        build_ws_payload(
            lead,
            match
        )
    )

    return True


# =========================================================
# DISPATCH ALL
# =========================================================

async def dispatch_new_lead(
    db: Session,
    lead_id
):

    matches = db.query(
        models.LeadMatch
    ).filter_by(
        lead_id=lead_id
    ).all()

    sent_count = 0

    for match in matches:

        ok = await dispatch_single_supplier(

            db,

            lead_id,

            match.supplier_id
        )

        if ok:
            sent_count += 1

    return {

        "success": True,

        "lead_id":
            str(lead_id),

        "sent_count":
            sent_count
    }


# =========================================================
# REDISPATCH
# =========================================================

async def redispatch_lead(
    db: Session,
    lead_id
):

    return await dispatch_new_lead(
        db,
        lead_id
    )


# =========================================================
# DISPATCH MATCH LIST
# =========================================================

async def dispatch_matches(
    db: Session,
    matches
):

    sent = 0

    for match in matches:

        ok = await dispatch_single_supplier(

            db,

            match.lead_id,

            match.supplier_id
        )

        if ok:
            sent += 1

    return sent