# services/auction_service.py

from datetime import datetime
from datetime import timedelta

from sqlalchemy.orm import Session

import models

from config import (
PRICING
)

from wallet.pricing import (
get_claim_cost
)

from wallet.service import (
deduct_credit
)

# =========================================================

# CREATE AUCTION

# =========================================================

def create_auction(

db: Session,

lead,

suppliers

):

ttl = PRICING.get(

    "auction_ttl",

    300
)

created = []

for supplier in suppliers:

    match = models.LeadMatch(

        lead_id=lead.id,

        supplier_id=supplier.id,

        distance_score=getattr(
            supplier,
            "distance_score",
            0
        ),

        reputation_score=getattr(
            supplier,
            "reputation_score",
            0
        ),

        speed_score=getattr(
            supplier,
            "speed_score",
            0
        ),

        price_score=0,

        base_score=getattr(
            supplier,
            "auction_base_score",
            0
        ),

        final_score=0,

        bid_price=None,

        status="pending",

        created_at=datetime.utcnow(),

        expires_at=(

            datetime.utcnow()

            +

            timedelta(
                seconds=ttl
            )
        )
    )

    db.add(match)

    created.append(match)

db.commit()

return created

# =========================================================

# GET MATCHES

# =========================================================

def get_auction_matches(

db: Session,

lead_id

):

return db.query(

    models.LeadMatch

).filter_by(

    lead_id=lead_id

).all()

# =========================================================

# ACTIVE

# =========================================================

def is_auction_active(

db: Session,

lead_id

):

now = datetime.utcnow()

matches = get_auction_matches(

    db,

    lead_id
)

for item in matches:

    if (

        item.status == "pending"

        and

        item.expires_at

        and

        item.expires_at > now
    ):

        return True

return False

# =========================================================

# AUCTION SCORE

# =========================================================

def calculate_auction_rank(

match

):

bid_price = (
    match.bid_price
    or
    0
)

return round(

    (match.base_score * 2)

    -

    (bid_price * 0.1),

    2
)

# =========================================================

# WINNER

# =========================================================

def select_auction_winner(

db: Session,

lead_id

):

matches = db.query(

    models.LeadMatch

).filter_by(

    lead_id=lead_id

).all()

candidates = []

for item in matches:

    if item.status != "pending":
        continue

    if item.bid_price is None:
        continue

    candidates.append(
        item
    )

if not candidates:
    return None

candidates.sort(

    key=calculate_auction_rank,

    reverse=True
)

return candidates[0]

# =========================================================

# FINALIZE

# =========================================================

def finalize_auction(

db: Session,

lead_id

):

winner = select_auction_winner(

    db,

    lead_id
)

if not winner:

    return {

        "success": False,

        "error": "no_winner"
    }

matches = db.query(

    models.LeadMatch

).filter_by(

    lead_id=lead_id

).all()

for item in matches:

    item.final_score = (
        calculate_auction_rank(
            item
        )
    )

winner.status = "won"

winner.won_at = datetime.utcnow()

losers = []

for item in matches:

    if item.id == winner.id:
        continue

    item.status = "lost"

    losers.append(
        item
    )

lead = db.query(

    models.Lead

).filter_by(

    id=lead_id

).first()

supplier = db.query(

    models.Supplier

).filter_by(

    id=winner.supplier_id

).first()

if supplier:

    supplier.wins = (

        supplier.wins
        or
        0

    ) + 1

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

    cost = get_claim_cost(

        lead_type,

        priority
    )

    deduct_credit(

        db=db,

        supplier_id=supplier.id,

        amount=cost,

        tx_type="auction_win",

        reference_id=str(
            lead_id
        )
    )

if lead:

    lead.status = "claimed"

db.commit()

return {

    "success": True,

    "lead_id":
        str(
            lead_id
        ),

    "winner_supplier_id":
        str(
            winner.supplier_id
        ),

    "winner_bid":
        winner.bid_price,

    "winner_score":
        winner.final_score
}

# =========================================================

# EXPIRE

# =========================================================

def expire_auction(

db: Session,

lead_id

):

now = datetime.utcnow()

count = 0

matches = db.query(

    models.LeadMatch

).filter_by(

    lead_id=lead_id,

    status="pending"
).all()

for item in matches:

    if (

        item.expires_at

        and

        item.expires_at < now
    ):

        item.status = "expired"

        count += 1

db.commit()

return count

# =========================================================

# AUTO FINALIZE

# =========================================================

def auto_finalize_expired_auctions(

db: Session

):

now = datetime.utcnow()

pending = db.query(

    models.LeadMatch

).filter(

    models.LeadMatch.status == "pending",

    models.LeadMatch.expires_at < now

).all()

lead_ids = set()

for item in pending:

    lead_ids.add(
        item.lead_id
    )

finalized = 0

for lead_id in lead_ids:

    result = finalize_auction(

        db,

        lead_id
    )

    if result.get(
        "success"
    ):

        finalized += 1

return finalized
