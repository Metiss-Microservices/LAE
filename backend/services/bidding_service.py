# services/bidding_service.py

from datetime import datetime

from sqlalchemy.orm import Session

import models

from services.auction_service import (
is_auction_active,
finalize_auction
)

def place_bid(

db: Session,

supplier_id,

lead_id,

bid_price

):

if bid_price is None:

    return {
        "success": False,
        "error": "invalid_bid"
    }

try:

    bid_price = float(
        bid_price
    )

except Exception:

    return {
        "success": False,
        "error": "invalid_bid"
    }

match = db.query(
    models.LeadMatch
).filter_by(

    supplier_id=supplier_id,

    lead_id=lead_id

).first()

if not match:

    return {
        "success": False,
        "error": "match_not_found"
    }

if match.status != "pending":

    return {
        "success": False,
        "error": "not_active"
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

match.bid_price = bid_price

db.commit()

return {

    "success": True,

    "lead_id":
        str(lead_id),

    "supplier_id":
        str(supplier_id),

    "bid_price":
        match.bid_price
}

def update_bid(

db: Session,

supplier_id,

lead_id,

new_price

):

return place_bid(

    db,

    supplier_id,

    lead_id,

    new_price
)

def get_bids(

db: Session,

lead_id

):

matches = db.query(
    models.LeadMatch
).filter_by(
    lead_id=lead_id
).all()

result = []

for m in matches:

    supplier = db.query(
        models.Supplier
    ).filter_by(
        id=m.supplier_id
    ).first()

    result.append({

        "supplier_id":
            str(m.supplier_id),

        "supplier_name":
            supplier.full_name
            if supplier
            else "-",

        "base_score":
            m.base_score,

        "final_score":
            m.final_score,

        "bid_price":
            m.bid_price,

        "status":
            m.status
    })

return result

def close_auction(

db: Session,

lead_id

):

return finalize_auction(
    db,
    lead_id
)

def auction_status(

db: Session,

lead_id

):

active = is_auction_active(
    db,
    lead_id
)

matches = db.query(
    models.LeadMatch
).filter_by(
    lead_id=lead_id
).count()

return {

    "lead_id":
        str(lead_id),

    "active":
        active,

    "matches":
        matches
}

def supplier_bid_info(

db: Session,

supplier_id,

lead_id

):

match = db.query(
    models.LeadMatch
).filter_by(

    supplier_id=supplier_id,

    lead_id=lead_id

).first()

if not match:
    return None

return {

    "supplier_id":
        str(supplier_id),

    "lead_id":
        str(lead_id),

    "base_score":
        match.base_score,

    "final_score":
        match.final_score,

    "bid_price":
        match.bid_price,

    "status":
        match.status,

    "expires_at":
        match.expires_at
}

def supplier_active_auctions(

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

for item in matches:

    if item.bid_price is None:
        continue

    result.append({

        "lead_id":
            str(item.lead_id),

        "match_id":
            str(item.id),

        "bid_price":
            item.bid_price,

        "score":
            item.final_score,

        "expires_at":
            item.expires_at
    })

return result
