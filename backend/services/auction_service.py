# services/auction_service.py

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

import models

from config import PRICING
from wallet.pricing import get_claim_cost
from wallet.service import deduct_credit


# =========================================================
# CREATE AUCTION
# =========================================================

def create_auction(
    db: Session,
    lead,
    suppliers,
):
    ttl = PRICING.get("auction_ttl", 300)

    created = []

    for supplier in suppliers:
        match = models.LeadMatch(
            lead_id=lead.id,
            supplier_id=supplier.id,
            distance_score=getattr(
                supplier,
                "distance_score",
                0,
            ),
            reputation_score=getattr(
                supplier,
                "reputation_score",
                0,
            ),
            speed_score=getattr(
                supplier,
                "speed_score",
                0,
            ),
            price_score=0,
            base_score=getattr(
                supplier,
                "auction_base_score",
                0,
            ),
            final_score=0,
            bid_price=None,
            status="pending",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(seconds=ttl),
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
    lead_id,
):
    return (
        db.query(models.LeadMatch)
        .filter_by(lead_id=lead_id)
        .all()
    )


# =========================================================
# ACTIVE
# =========================================================

def is_auction_active(
    db: Session,
    lead_id,
):
    now = datetime.utcnow()

    matches = get_auction_matches(
        db,
        lead_id,
    )

    for item in matches:
        if (
            item.status == "pending"
            and item.expires_at
            and item.expires_at > now
        ):
            return True

    return False


# =========================================================
# AUCTION SCORE
# =========================================================

def calculate_auction_rank(match):
    bid_price = match.bid_price or 0

    return round(
        (match.base_score * 2)
        - (bid_price * 0.1),
        2,
    )


# =========================================================
# WINNER
# =========================================================

def select_auction_winner(
    db: Session,
    lead_id,
):
    matches = (
        db.query(models.LeadMatch)
        .filter(
            models.LeadMatch.lead_id == lead_id,
            models.LeadMatch.status == "pending",
        )
        .with_for_update()
        .all()
    )

    candidates = []

    for item in matches:
        bid_price = item.bid_price

        # فقط Bid واقعی و مثبت وارد Auction شود.
        if bid_price is None:
            continue

        if float(bid_price) <= 0:
            continue

        candidates.append(item)

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: (
            calculate_auction_rank(item),
            item.created_at,
        ),
        reverse=True,
    )

    return candidates[0]

# =========================================================
# FINALIZE
# =========================================================

def finalize_auction(
    db: Session,
    lead_id,
):
    winner = select_auction_winner(
        db,
        lead_id,
    )

    if not winner:
        return {
            "success": False,
            "error": "no_winner",
        }

    lead = (
        db.query(models.Lead)
        .filter_by(id=lead_id)
        .with_for_update()
        .first()
    )

    if not lead:
        return {
            "success": False,
            "error": "lead_not_found",
        }

    # جلوگیری از Finalize مجدد و کسر اعتبار تکراری
    if (
        lead.status == "claimed"
        and lead.winner_supplier_id
    ):
        return {
            "success": False,
            "error": "already_finalized",
        }

    matches = (
        db.query(models.LeadMatch)
        .filter_by(lead_id=lead_id)
        .with_for_update()
        .all()
    )

    finalized_at = datetime.utcnow()

    for item in matches:
        item.final_score = calculate_auction_rank(
            item
        )

        if item.id == winner.id:
            item.status = "won"
            item.won_at = finalized_at
        else:
            item.status = "lost"

    supplier = (
        db.query(models.Supplier)
        .filter_by(id=winner.supplier_id)
        .with_for_update()
        .first()
    )

    if not supplier:
        db.rollback()

        return {
            "success": False,
            "error": "supplier_not_found",
        }

    lead_type = getattr(
        lead,
        "lead_type",
        "service",
    )

    priority = getattr(
        lead,
        "priority_level",
        "medium",
    )

    cost = get_claim_cost(
        lead_type,
        priority,
    )

    credit_ok = deduct_credit(
        db=db,
        supplier_id=supplier.id,
        amount=cost,
        tx_type="auction_win",
        reference_id=str(winner.id),
        description="auction win",
    )

    if not credit_ok:
        db.rollback()

        return {
            "success": False,
            "error": "insufficient_credit",
        }

    supplier.wins = (
        supplier.wins or 0
    ) + 1

    lead.status = "claimed"
    lead.winner_supplier_id = winner.supplier_id
    lead.closed_at = finalized_at

    # فقط اگر این ستون در مدل وجود دارد
    if hasattr(lead, "winner_match_id"):
        lead.winner_match_id = winner.id

    db.commit()

    return {
        "success": True,
        "lead_id": str(lead.id),
        "winner_supplier_id": str(
            winner.supplier_id
        ),
        "winner_match_id": str(
            winner.id
        ),
        "winner_bid": float(
            winner.bid_price or 0
        ),
        "winner_score": float(
            winner.final_score or 0
        ),
        "closed_at": (
            lead.closed_at.isoformat()
            if lead.closed_at
            else None
        ),
    }
# =========================================================
# EXPIRE
# =========================================================

def expire_auction(
    db: Session,
    lead_id,
):
    now = datetime.utcnow()

    count = 0

    matches = (
        db.query(models.LeadMatch)
        .filter_by(
            lead_id=lead_id,
            status="pending",
        )
        .all()
    )

    for item in matches:
        if (
            item.expires_at
            and item.expires_at < now
        ):
            item.status = "expired"
            count += 1

    db.commit()

    return count


# =========================================================
# AUTO FINALIZE
# =========================================================

def auto_finalize_expired_auctions(
    db: Session,
):
    now = datetime.utcnow()

    pending = (
        db.query(models.LeadMatch)
        .filter(
            models.LeadMatch.status == "pending",
            models.LeadMatch.expires_at.isnot(None),
            models.LeadMatch.expires_at < now,
        )
        .all()
    )

    lead_ids = {
        item.lead_id
        for item in pending
    }

    finalized = 0
    expired = 0

    for lead_id in lead_ids:
        result = finalize_auction(
            db,
            lead_id,
        )

        if result.get("success"):
            finalized += 1
            continue

        # No valid bid/winner: expire all remaining pending matches.
        rows = (
            db.query(models.LeadMatch)
            .filter(
                models.LeadMatch.lead_id == lead_id,
                models.LeadMatch.status == "pending",
                models.LeadMatch.expires_at.isnot(None),
                models.LeadMatch.expires_at < now,
            )
            .all()
        )

        for row in rows:
            row.status = "expired"
            expired += 1

        db.commit()

    return {
        "finalized": finalized,
        "expired": expired,
    }