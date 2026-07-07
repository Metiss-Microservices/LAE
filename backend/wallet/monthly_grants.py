from datetime import datetime
from datetime import timedelta

from sqlalchemy.orm import Session

import models

from wallet.service import add_credit


# =========================================================
# MONTHLY FREE CREDIT
# =========================================================

MONTHLY_FREE_CREDIT = 10


# =========================================================
# ELIGIBLE
# =========================================================

def is_eligible_for_monthly_grant(
    supplier
):

    last = getattr(
        supplier,
        "last_monthly_grant_at",
        None
    )

    if not last:
        return True

    return (
        datetime.utcnow() - last
    ) >= timedelta(days=30)


# =========================================================
# GRANT ONE
# =========================================================

def grant_monthly_credit(
    db: Session,
    supplier
):

    if not is_eligible_for_monthly_grant(
        supplier
    ):
        return False

    add_credit(

        db=db,

        supplier_id=supplier.id,

        amount=MONTHLY_FREE_CREDIT,

        tx_type="monthly_grant",

        reference_id="monthly_grant"
    )

    supplier.last_monthly_grant_at = (
        datetime.utcnow()
    )

    db.commit()

    return True


# =========================================================
# GRANT ALL
# =========================================================

def run_monthly_grants(
    db: Session
):

    suppliers = db.query(
        models.Supplier
    ).filter(

        models.Supplier.is_active == True,

        models.Supplier.is_blocked == False

    ).all()

    count = 0

    for supplier in suppliers:

        if grant_monthly_credit(
            db,
            supplier
        ):
            count += 1

    return count