from datetime import datetime

from sqlalchemy.orm import Session

import models

from wallet.service import deduct_credit

from websocket.events import (
    emit_lead_claimed,
    emit_lead_lost,
)

from config import PRICING


# =========================================================
# CLAIM LEAD
# =========================================================

async def claim_lead(
    db: Session,
    supplier_id,
    match_id,
):
    now = datetime.utcnow()

    match = (
        db.query(models.LeadMatch)
        .filter_by(
            id=match_id,
            supplier_id=supplier_id,
        )
        .with_for_update()
        .first()
    )

    if not match:
        return {
            "success": False,
            "error": "match_not_found",
        }

    if match.status != "pending":
        return {
            "success": False,
            "error": "already_processed",
        }

    if (
        match.expires_at
        and match.expires_at < now
    ):
        match.status = "expired"
        db.commit()

        return {
            "success": False,
            "error": "expired",
        }

    supplier = (
        db.query(models.Supplier)
        .filter_by(id=supplier_id)
        .first()
    )

    if not supplier:
        return {
            "success": False,
            "error": "supplier_not_found",
        }

    lead = (
        db.query(models.Lead)
        .filter_by(id=match.lead_id)
        .with_for_update()
        .first()
    )

    if not lead:
        return {
            "success": False,
            "error": "lead_not_found",
        }

    if lead.status not in (
        "open",
        "matched",
        "auction",
    ):
        return {
            "success": False,
            "error": "lead_not_available",
        }

    claim_cost = PRICING.get(
        "claim_cost",
        1,
    )

    ok = deduct_credit(
        db=db,
        supplier_id=supplier.id,
        amount=claim_cost,
        tx_type="lead_claim",
        reference_id=str(match.id),
        description="lead claim",
    )

    if not ok:
        return {
            "success": False,
            "error": "insufficient_credit",
        }

    # -----------------------------------------------------
    # WINNER
    # -----------------------------------------------------

    match.status = "won"
    match.won_at = now

    supplier.wins = (
        supplier.wins or 0
    ) + 1

    # -----------------------------------------------------
    # LEAD FINALIZATION
    # -----------------------------------------------------

    lead.status = "claimed"
    lead.winner_supplier_id = supplier.id
    lead.closed_at = now

    # -----------------------------------------------------
    # LOSERS
    # -----------------------------------------------------

    others = (
        db.query(models.LeadMatch)
        .filter(
            models.LeadMatch.lead_id
            == match.lead_id,
            models.LeadMatch.id
            != match.id,
            models.LeadMatch.status
            == "pending",
        )
        .with_for_update()
        .all()
    )

    for item in others:
        item.status = "lost"

    db.commit()

    db.refresh(match)
    db.refresh(supplier)
    db.refresh(lead)

    # -----------------------------------------------------
    # WEBSOCKET EVENTS
    # -----------------------------------------------------

    for item in others:
        try:
            await emit_lead_lost(
                item.supplier_id,
                match.lead_id,
            )
        except Exception:
            pass

    try:
        await emit_lead_claimed(
            supplier.id,
            match.lead_id,
        )
    except Exception:
        pass

    # -----------------------------------------------------
    # CLIENT
    # -----------------------------------------------------

    client = (
        db.query(models.Client)
        .filter_by(id=lead.client_id)
        .first()
    )

    return {
        "success": True,
        "status": "won",
        "lead_id": str(lead.id),
        "winner_supplier_id": str(
            supplier.id
        ),
        "client_phone": (
            client.phone
            if client
            else None
        ),
        "remaining_credit": (
            supplier.credit_balance or 0
        ),
    }