from sqlalchemy.orm import Session

from scoring.service import (
    add_review,
    sync_supplier_metrics
)


# =========================================================
# RATE SUPPLIER
# =========================================================

def rate_supplier(

    db: Session,

    supplier_id,

    rating,

    review=None,

    client_id=None,

    lead_id=None
):

    ok = add_review(

        db=db,

        supplier_id=supplier_id,

        rating=rating,

        review=review,

        client_id=client_id,

        lead_id=lead_id
    )

    if not ok:
        return False

    sync_supplier_metrics(
        db,
        supplier_id
    )

    return True
