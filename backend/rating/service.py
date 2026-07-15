from sqlalchemy.orm import Session

from models import (
    Supplier,
    SupplierReview,
    Lead,
    LeadMatch,
)

# =========================================================
# CAN REVIEW
# =========================================================

def can_review(
    db: Session,
    supplier_id,
    client_id,
    lead_id,
):
    lead = (
        db.query(Lead)
        .filter_by(
            id=lead_id,
            client_id=client_id,
            winner_supplier_id=supplier_id,
            status="claimed",
        )
        .first()
    )

    if not lead:
        return False

    match = (
        db.query(LeadMatch)
        .filter_by(
            lead_id=lead_id,
            supplier_id=supplier_id,
            status="won",
        )
        .first()
    )

    if not match:
        return False

    existing = (
        db.query(SupplierReview)
        .filter_by(
            supplier_id=supplier_id,
            client_id=client_id,
            lead_id=lead_id,
        )
        .first()
    )

    if existing:
        return False

    return True

# =========================================================
# UPDATE SUPPLIER SCORE
# =========================================================

def recalculate_supplier_score(
    db: Session,
    supplier_id
):

    supplier = db.query(
        Supplier
    ).filter_by(
        id=supplier_id
    ).first()

    if not supplier:
        return

    reviews = db.query(
        SupplierReview
    ).filter_by(
        supplier_id=supplier_id
    ).all()

    if not reviews:

        supplier.score = 0
        supplier.rating_count = 0

        return

    total = sum(
        r.rating
        for r in reviews
    )

    count = len(reviews)

    supplier.score = round(
        total / count,
        2
    )

    supplier.rating_count = count


# =========================================================
# CREATE REVIEW
# =========================================================

def create_review(

    db: Session,

    supplier_id,

    client_id,

    lead_id,

    rating,

    comment=None
):

    supplier = db.query(
        Supplier
    ).filter_by(
        id=supplier_id
    ).first()

    if not supplier:

        return {
            "success": False,
            "error": "supplier_not_found"
        }

    if not can_review(

        db,

        supplier_id,

        client_id,

        lead_id
    ):

        return {
            "success": False,
            "error": "review_not_allowed"
        }

    review = SupplierReview(

        supplier_id=supplier_id,

        client_id=client_id,

        lead_id=lead_id,

        rating=float(rating),

        comment=comment
    )

    db.add(review)

    db.flush()

    recalculate_supplier_score(

        db,

        supplier_id
    )

    db.commit()

    return {
        "success": True,
        "review_id": str(review.id)
    }


# =========================================================
# GET REVIEWS
# =========================================================

def get_supplier_reviews(

    db: Session,

    supplier_id,

    limit=50
):

    rows = db.query(
        SupplierReview
    ).filter_by(
        supplier_id=supplier_id
    ).order_by(
        SupplierReview.created_at.desc()
    ).limit(
        limit
    ).all()

    result = []

    for row in rows:

        result.append({

            "id":
                str(row.id),

            "lead_id":
                str(row.lead_id),

            "rating":
                row.rating,

            "comment":
                row.comment,

            "created_at":
                row.created_at
        })

    return result