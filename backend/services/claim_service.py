from datetime import datetime

from sqlalchemy.orm import Session

import models

from wallet.service import deduct_credit

from websocket.events import (
    emit_lead_claimed,
    emit_lead_lost
)

from config import PRICING


async def claim_lead(
    db: Session,
    supplier_id,
    match_id
):

    match = db.query(
        models.LeadMatch
    ).filter_by(
        id=match_id,
        supplier_id=supplier_id
    ).with_for_update().first()

    if not match:

        return {
            "success": False,
            "error": "match_not_found"
        }

    if match.status != "pending":

        return {
            "success": False,
            "error": "already_processed"
        }

    if (
        match.expires_at
        and
        match.expires_at < datetime.utcnow()
    ):

        match.status = "expired"

        db.commit()

        return {
            "success": False,
            "error": "expired"
        }

    supplier = db.query(
        models.Supplier
    ).filter_by(
        id=supplier_id
    ).first()

    if not supplier:

        return {
            "success": False,
            "error": "supplier_not_found"
        }

    claim_cost = PRICING.get(
        "claim_cost",
        1
    )

    ok = deduct_credit(

        db=db,

        supplier_id=supplier.id,

        amount=claim_cost,

        tx_type="lead_claim",

        reference_id=str(match.id),

        description="lead claim"
    )

    if not ok:

        return {
            "success": False,
            "error": "insufficient_credit"
        }

    match.status = "won"

    match.won_at = datetime.utcnow()

    supplier.wins = (
        supplier.wins or 0
    ) + 1

    others = db.query(
        models.LeadMatch
    ).filter(

        models.LeadMatch.lead_id
        ==
        match.lead_id,

        models.LeadMatch.id
        !=
        match.id
    ).all()

    for item in others:

        item.status = "lost"

    db.commit()

    for item in others:

        try:

            await emit_lead_lost(
                item.supplier_id,
                match.lead_id
            )

        except:
            pass

    try:

        await emit_lead_claimed(
            supplier_id,
            match.lead_id
        )

    except:
        pass

    lead = db.query(
        models.Lead
    ).filter_by(
        id=match.lead_id
    ).first()

    client = None

    if lead:

        client = db.query(
            models.Client
        ).filter_by(
            id=lead.client_id
        ).first()

    return {

        "success": True,

        "status": "won",

        "lead_id":
            str(match.lead_id),

        "client_phone":
            client.phone
            if client
            else None,

        "remaining_credit":
            supplier.credit_balance
    }