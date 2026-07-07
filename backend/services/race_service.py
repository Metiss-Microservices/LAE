# services/race_service.py

from datetime import datetime

from sqlalchemy.orm import Session

import models

from wallet.pricing import (
get_claim_cost
)

from wallet.service import (
deduct_credit
)

from websocket.events import (
emit_lead_claimed,
emit_lead_lost,
emit_credit_update
)

# =========================================================

# GET MATCH

# =========================================================

def get_match(

db: Session,

match_id

):

return db.query(

    models.LeadMatch

).filter_by(

    id=match_id

).first()

# =========================================================

# EXPIRED

# =========================================================

def is_expired(

match

):

if not match.expires_at:
    return False

return (

    match.expires_at

    <

    datetime.utcnow()
)

# =========================================================

# MARK EXPIRED

# =========================================================

def expire_match(

db: Session,

match

):

match.status = "expired"

db.commit()

# =========================================================

# CLOSE LOSERS

# =========================================================

def close_other_matches(

db: Session,

lead_id,

winner_match_id

):

losers = db.query(

    models.LeadMatch

).filter(

    models.LeadMatch.lead_id == lead_id,

    models.LeadMatch.id != winner_match_id

).all()

for item in losers:

    item.status = "lost"

return losers

# =========================================================

# CLIENT INFO

# =========================================================

def get_client_data(

db: Session,

lead_id

):

lead = db.query(

    models.Lead

).filter_by(

    id=lead_id

).first()

if not lead:
    return None

client = db.query(

    models.Client

).filter_by(

    id=lead.client_id

).first()

if not client:
    return None

return {

    "client_id":
        str(client.id),

    "name":
        client.full_name,

    "phone":
        client.phone
}

# =========================================================

# CLAIM

# =========================================================

async def claim_race_lead(

db: Session,

supplier_id,

match_id

):

match = get_match(

    db,

    match_id
)

if not match:

    return {

        "success": False,

        "error": "match_not_found"
    }

if str(match.supplier_id) != str(supplier_id):

    return {

        "success": False,

        "error": "access_denied"
    }

if match.status != "pending":

    return {

        "success": False,

        "error": "already_processed"
    }

if is_expired(match):

    expire_match(

        db,

        match
    )

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

lead = db.query(

    models.Lead

).filter_by(

    id=match.lead_id

).first()

if not lead:

    return {

        "success": False,

        "error": "lead_not_found"
    }

lead_type = getattr(

    lead,

    "lead_type",

    "service"
)

priority = getattr(

    lead,

    "priority_level",

    "medium"
)

credit_cost = get_claim_cost(

    lead_type,

    priority
)

if (

    (supplier.credit_balance or 0)

    <

    credit_cost
):

    return {

        "success": False,

        "error": "insufficient_credit"
    }

deducted = deduct_credit(

    db=db,

    supplier_id=supplier.id,

    amount=credit_cost,

    tx_type="lead_claim",

    reference_id=str(
        match.id
    )
)

if not deducted:

    return {

        "success": False,

        "error": "credit_deduct_failed"
    }

supplier.wins = (

    supplier.wins
    or
    0

) + 1

match.status = "won"

match.won_at = datetime.utcnow()

losers = close_other_matches(

    db,

    match.lead_id,

    match.id
)

lead.status = "claimed"

db.commit()

try:

    await emit_credit_update(

        supplier.id,

        supplier.credit_balance
    )

    await emit_lead_claimed(

        supplier.id,

        match.lead_id
    )

    for loser in losers:

        await emit_lead_lost(

            loser.supplier_id,

            loser.lead_id
        )

except Exception:

    pass

client_data = get_client_data(

    db,

    match.lead_id
)

return {

    "success": True,

    "lead_id":
        str(match.lead_id),

    "match_id":
        str(match.id),

    "credit_cost":
        credit_cost,

    "remaining_credit":
        supplier.credit_balance,

    "client":
        client_data
}

# =========================================================

# ACTIVE RACES

# =========================================================

def get_active_races(

db: Session,

supplier_id

):

matches = db.query(

    models.LeadMatch

).filter_by(

    supplier_id=supplier_id,

    status="pending"
).all()

result = []

now = datetime.utcnow()

changed = False

for item in matches:

    if is_expired(item):

        item.status = "expired"

        changed = True

        continue

    remaining = int(

        (

            item.expires_at

            -

            now

        ).total_seconds()
    )

    result.append({

        "match_id":
            str(item.id),

        "lead_id":
            str(item.lead_id),

        "score":
            item.final_score,

        "remaining":
            max(
                remaining,
                0
            )
    })

if changed:

    db.commit()

return result
