from datetime import datetime

from sqlalchemy.orm import Session

from models import (

    Supplier,

    SupplierReview
)

from scoring.reputation import (

    calculate_average_rating,

    calculate_trust_score,

    calculate_success_rate,

    review_count
)


# =========================================================
# ADD REVIEW
# =========================================================

def add_review(

    db: Session,

    supplier_id,

    rating,

    review=None,

    client_id=None,

    lead_id=None
):

    supplier = db.query(
        Supplier
    ).filter_by(
        id=supplier_id
    ).first()

    if not supplier:
        return False

    row = SupplierReview(

        supplier_id=supplier_id,

        client_id=client_id,

        lead_id=lead_id,

        rating=rating,

        review=review,

        created_at=datetime.utcnow()
    )

    db.add(row)

    db.commit()

    sync_supplier_metrics(
        db,
        supplier_id
    )

    return True


# =========================================================
# UPDATE SUPPLIER SCORE
# =========================================================

def update_supplier_score(
    db: Session,
    supplier_id
):

    supplier = db.query(
        Supplier
    ).filter_by(
        id=supplier_id
    ).first()

    if not supplier:
        return False

    avg_rating = calculate_average_rating(
        db,
        supplier_id
    )

    supplier.score = avg_rating

    db.commit()

    return True


# =========================================================
# SUPPLIER REPUTATION OBJECT
# =========================================================

def calculate_supplier_reputation(
    db: Session,
    supplier_id
):

    supplier = db.query(
        Supplier
    ).filter_by(
        id=supplier_id
    ).first()

    if not supplier:

        return {

            "rating_avg": 0,

            "review_count": 0,

            "trust_score": 0,

            "success_rate": 0,

            "wins": 0
        }

    rating_avg = calculate_average_rating(
        db,
        supplier_id
    )

    reviews_total = review_count(
        db,
        supplier_id
    )

    trust_score = calculate_trust_score(
        db,
        supplier_id
    )

    success_rate = calculate_success_rate(
        db,
        supplier_id
    )

    return {

        "rating_avg":
            rating_avg,

        "review_count":
            reviews_total,

        "trust_score":
            trust_score,

        "success_rate":
            success_rate,

        "wins":
            supplier.wins or 0
    }


# =========================================================
# SYNC METRICS
# =========================================================

def sync_supplier_metrics(
    db: Session,
    supplier_id
):

    supplier = db.query(
        Supplier
    ).filter_by(
        id=supplier_id
    ).first()

    if not supplier:
        return False

    reputation = calculate_supplier_reputation(
        db,
        supplier_id
    )

    supplier.score = (
        reputation["rating_avg"]
    )

    supplier.reputation_score = (
        reputation["trust_score"]
    )

    supplier.trust_score = (
        reputation["trust_score"]
    )

    supplier.success_rate = (
        reputation["success_rate"]
    )

    supplier.rating_count = (
        reputation["review_count"]
    )

    db.commit()

    return True