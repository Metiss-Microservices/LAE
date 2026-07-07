from sqlalchemy.orm import Session

from models import (
    Supplier,
    SupplierReview,
    LeadMatch
)


# =========================================================
# AVERAGE RATING
# =========================================================

def calculate_average_rating(
    db: Session,
    supplier_id
):

    reviews = db.query(
        SupplierReview
    ).filter_by(
        supplier_id=supplier_id
    ).all()

    if not reviews:
        return 5.0

    total = sum(
        r.rating
        for r in reviews
    )

    return round(
        total / len(reviews),
        2
    )


# =========================================================
# REVIEW COUNT
# =========================================================

def review_count(
    db: Session,
    supplier_id
):

    return db.query(
        SupplierReview
    ).filter_by(
        supplier_id=supplier_id
    ).count()


# =========================================================
# TOTAL WINS
# =========================================================

def calculate_total_wins(
    db: Session,
    supplier_id
):

    supplier = db.query(
        Supplier
    ).filter_by(
        id=supplier_id
    ).first()

    if not supplier:
        return 0

    return supplier.wins or 0


# =========================================================
# SUCCESS RATE
# =========================================================

def calculate_success_rate(
    db: Session,
    supplier_id
):

    total = db.query(
        LeadMatch
    ).filter_by(
        supplier_id=supplier_id
    ).count()

    if total <= 0:
        return 0

    wins = db.query(
        LeadMatch
    ).filter_by(
        supplier_id=supplier_id,
        status="won"
    ).count()

    return round(
        (wins / total) * 100,
        2
    )


# =========================================================
# TRUST SCORE
# =========================================================

def calculate_trust_score(
    db: Session,
    supplier_id
):

    supplier = db.query(
        Supplier
    ).filter_by(
        id=supplier_id
    ).first()

    if not supplier:
        return 0

    rating = calculate_average_rating(
        db,
        supplier_id
    )

    success_rate = calculate_success_rate(
        db,
        supplier_id
    )

    wins = calculate_total_wins(
        db,
        supplier_id
    )

    reviews = review_count(
        db,
        supplier_id
    )

    verified_bonus = (
        15
        if supplier.is_verified
        else 0
    )

    score = 0

    score += rating * 15

    score += success_rate * 0.45

    score += min(
        wins,
        100
    ) * 1.0

    score += min(
        reviews,
        100
    ) * 0.4

    score += verified_bonus

    return round(
        score,
        2
    )


# =========================================================
# SUMMARY
# =========================================================

def reputation_summary(
    db: Session,
    supplier_id
):

    return {

        "rating":
            calculate_average_rating(
                db,
                supplier_id
            ),

        "review_count":
            review_count(
                db,
                supplier_id
            ),

        "success_rate":
            calculate_success_rate(
                db,
                supplier_id
            ),

        "wins":
            calculate_total_wins(
                db,
                supplier_id
            ),

        "trust_score":
            calculate_trust_score(
                db,
                supplier_id
            )
    }