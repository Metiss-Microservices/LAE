# services/matching_service.py

from datetime import datetime
from datetime import timedelta

from sqlalchemy.orm import Session

import models

from config import (
    MATCH_LIMIT,
    PRICING
)

from scoring.reputation import (
    calculate_trust_score,
    calculate_success_rate
)

from scoring.matching import (
    calculate_priority_multiplier
)

from services.auction_service import (
    create_auction
)

# =========================================================

# LOCATION CHAIN

# =========================================================

def get_location_chain(db: Session, location_id):
    loc = db.query(
        models.Location
    ).filter_by(
        id=location_id
    ).first()

    chain = {
        "district": None,
        "city": None,
        "province": None
    }

    while loc:
        if loc.type == "district":
            chain["district"] = loc.id
        elif loc.type == "city":
            chain["city"] = loc.id
        elif loc.type == "province":
            chain["province"] = loc.id

        if not loc.parent_id:
            break

        loc = db.query(
            models.Location
        ).filter_by(
            id=loc.parent_id
        ).first()

    return chain


# =========================================================

# LOCATION SCORE

# =========================================================

def location_score(lead_chain, supplier_chain):
    if (
        lead_chain["district"]
        and supplier_chain["district"]
        and lead_chain["district"] == supplier_chain["district"]
    ):
        return 60

    if (
        lead_chain["city"]
        and supplier_chain["city"]
        and lead_chain["city"] == supplier_chain["city"]
    ):
        return 40

    if (
        lead_chain["province"]
        and supplier_chain["province"]
        and lead_chain["province"] == supplier_chain["province"]
    ):
        return 20

    return 0


# =========================================================

# RESPONSE SCORE

# =========================================================

def response_score(supplier):
    speed = getattr(supplier, "response_speed", 60)

    if speed <= 15:
        return 25

    if speed <= 30:
        return 18

    if speed <= 60:
        return 10

    if speed <= 120:
        return 5

    return 0


# =========================================================

# REPUTATION SCORE

# =========================================================

def reputation_score(db, supplier):
    trust = calculate_trust_score(db, supplier.id)
    success_rate = calculate_success_rate(db, supplier.id)

    score = 0
    score += trust * 5
    score += success_rate * 0.5
    score += (supplier.score or 0) * 8
    score += (supplier.wins or 0) * 1.5

    return round(score, 2)


# =========================================================

# ELIGIBILITY

# =========================================================

def is_supplier_eligible(supplier):
    if not supplier:
        return False

    if not supplier.is_active:
        return False

    if getattr(supplier, "is_blocked", False):
        return False

    return True


# =========================================================

# SCORE

# =========================================================

def calculate_score(db, lead, supplier):
    lead_chain = get_location_chain(db, lead.location_id)
    supplier_chain = get_location_chain(db, supplier.location_id)

    loc_score = location_score(lead_chain, supplier_chain)
    rep_score = reputation_score(db, supplier)
    speed_score_value = response_score(supplier)

    total = calculate_priority_multiplier(
        lead.priority_mode,
        loc_score,
        rep_score,
        speed_score_value,
        0
    )

    return {
        "distance_score": loc_score,
        "reputation_score": rep_score,
        "speed_score": speed_score_value,
        "price_score": 0,
        "final_score": round(total, 2)
    }


# =========================================================

# CREATE RACE MATCH

# =========================================================

def create_race_match(db, lead, supplier, score_data):
    ttl = PRICING.get("race_ttl", 120)

    match = models.LeadMatch(
        lead_id=lead.id,
        supplier_id=supplier.id,
        distance_score=score_data["distance_score"],
        reputation_score=score_data["reputation_score"],
        speed_score=score_data["speed_score"],
        price_score=score_data["price_score"],
        base_score=score_data["final_score"],
        final_score=score_data["final_score"],
        status="pending",
        created_at=datetime.utcnow(),
        expires_at=(
            datetime.utcnow()
            + timedelta(seconds=ttl)
        )
    )

    db.add(match)
    return match


# =========================================================
# SUPPLIER CANDIDATES
# =========================================================

def get_candidate_suppliers(db, lead):
    # exact category + subcategory
    exact_rows = (
        db.query(
            models.Supplier
        )
        .join(
            models.SupplierCategory,
            models.Supplier.id
            == models.SupplierCategory.supplier_id
        )
        .filter(
            models.SupplierCategory.category_id == lead.category_id,
            models.SupplierCategory.subcategory_id == lead.subcategory_id
        )
        .distinct()
        .all()
    )

    if exact_rows:
        return exact_rows

    # category only
    category_rows = (
        db.query(
            models.Supplier
        )
        .join(
            models.SupplierCategory,
            models.Supplier.id
            == models.SupplierCategory.supplier_id
        )
        .filter(
            models.SupplierCategory.category_id == lead.category_id
        )
        .distinct()
        .all()
    )

    return category_rows


# =========================================================

# AUCTION FLOW

# =========================================================

def run_auction_matching(db, lead, scored):
    scored.sort(
        key=lambda x: x["score_data"]["final_score"],
        reverse=True
    )

    top = scored[:MATCH_LIMIT]
    suppliers = []

    for item in top:
        supplier = item["supplier"]
        supplier.auction_base_score = item["score_data"]["final_score"]
        supplier.distance_score = item["score_data"]["distance_score"]
        supplier.reputation_score = item["score_data"]["reputation_score"]
        supplier.speed_score = item["score_data"]["speed_score"]
        suppliers.append(supplier)

    return create_auction(db=db, lead=lead, suppliers=suppliers)


# =========================================================

# RACE FLOW

# =========================================================

def run_race_matching(db, lead, scored):
    scored.sort(
        key=lambda x: x["score_data"]["final_score"],
        reverse=True
    )

    top = scored[:MATCH_LIMIT]
    matches = []

    for item in top:
        match = create_race_match(
            db,
            lead,
            item["supplier"],
            item["score_data"]
        )
        matches.append(match)

    db.commit()
    return matches


# =========================================================

# MAIN ENTRY

# =========================================================

def match_lead(db: Session, lead_id):
    lead = db.query(
        models.Lead
    ).filter_by(
        id=lead_id
    ).first()

    if not lead:
        return []

    suppliers = get_candidate_suppliers(db, lead)

    if not suppliers:
        return []

    scored = []

    for supplier in suppliers:
        if not is_supplier_eligible(supplier):
            continue

        score_data = calculate_score(db, lead, supplier)

        scored.append({
            "supplier": supplier,
            "score_data": score_data
        })

    if not scored:
        return []

    # CHEAPEST => AUCTION
    if lead.priority_mode == "cheapest":
        return run_auction_matching(db, lead, scored)

    # SMART / NEAREST / EXPERIENCED
    return run_race_matching(db, lead, scored)
