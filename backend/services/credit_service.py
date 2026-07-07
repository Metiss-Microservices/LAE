from models import Supplier, CreditTransaction
from sqlalchemy.orm import Session
from datetime import datetime


def consume(db: Session, supplier_id, amount: int, ref) -> bool:
    try:
        # 🔒 lock supplier row (important for concurrency)
        supplier = (
            db.query(Supplier)
            .filter_by(id=supplier_id)
            .with_for_update()
            .first()
        )

        if not supplier:
            return False

        if supplier.credit_balance < amount:
            return False

        # 💳 deduct credit
        supplier.credit_balance -= amount

        # 🧾 transaction log
        tx = CreditTransaction(
            supplier_id=supplier_id,
            amount=-amount,
            type="lead_claim",
            reference_id=str(ref),
            created_at=datetime.utcnow()
        )

        db.add(tx)

        return True

    except Exception as e:
        # ❗ مهم: اینجا commit نداریم، ولی باید fail safe باشیم
        db.rollback()
        return False