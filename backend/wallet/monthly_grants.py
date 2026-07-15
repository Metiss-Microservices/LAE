from datetime import datetime, timedelta

from sqlalchemy.orm import Session

import models

from wallet.service import add_credit


# =========================================================
# MONTHLY FREE CREDIT
# =========================================================

MONTHLY_FREE_CREDIT = 10
GRANT_INTERVAL_DAYS = 30


# =========================================================
# ELIGIBLE
# =========================================================

def is_eligible_for_monthly_grant(
    supplier,
    now: datetime | None = None,
):
    now = now or datetime.utcnow()

    last_grant_at = getattr(
        supplier,
        "last_free_credit_at",
        None,
    )

    if not last_grant_at:
        return True

    return (
        now - last_grant_at
    ) >= timedelta(
        days=GRANT_INTERVAL_DAYS
    )


# =========================================================
# GRANT ONE
# =========================================================

def grant_monthly_credit(
    db: Session,
    supplier,
):
    now = datetime.utcnow()

    if not is_eligible_for_monthly_grant(
        supplier,
        now,
    ):
        return False

    add_credit(
        db=db,
        supplier_id=supplier.id,
        amount=MONTHLY_FREE_CREDIT,
        tx_type="monthly_grant",
        reference_id="monthly_grant",
    )

    supplier.last_free_credit_at = now

    db.commit()
    db.refresh(supplier)

    return True


# =========================================================
# GRANT ALL
# =========================================================

def run_monthly_grants(
    db: Session,
):
    suppliers = (
        db.query(models.Supplier)
        .filter(
            models.Supplier.is_active.is_(True),
            models.Supplier.is_blocked.is_(False),
        )
        .all()
    )

    granted_count = 0

    for supplier in suppliers:
        try:
            granted = grant_monthly_credit(
                db,
                supplier,
            )

            if granted:
                granted_count += 1

        except Exception:
            db.rollback()
            raise

    return granted_count