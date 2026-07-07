from sqlalchemy.orm import Session

from models import Supplier


# =========================================================
# GET SUPPLIER
# =========================================================

def get_supplier(
    db: Session,
    supplier_id
):

    return db.query(
        Supplier
    ).filter_by(
        id=supplier_id
    ).first()


# =========================================================
# UPDATE RESPONSE SPEED
# =========================================================

def update_response_speed(

    db: Session,

    supplier_id,

    seconds
):

    supplier = db.query(
        Supplier
    ).filter_by(
        id=supplier_id
    ).first()

    if not supplier:
        return False

    current = (
        supplier.response_speed or 0
    )

    if current <= 0:

        supplier.response_speed = seconds

    else:

        supplier.response_speed = round(

            (current + seconds) / 2,

            2
        )

    db.commit()

    return True


# =========================================================
# INCREMENT TOTAL JOBS
# =========================================================

def increment_total_jobs(
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

    supplier.total_jobs = (
        supplier.total_jobs or 0
    ) + 1

    db.commit()

    return True
