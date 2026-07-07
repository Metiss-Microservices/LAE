from sqlalchemy.orm import Session
from models import Supplier, CreditTransaction


def check_credit(db: Session, supplier_id: int) -> bool:
    supplier = db.query(Supplier).get(supplier_id)

    if not supplier:
        return False

    return supplier.credit > 0


def consume_credit(db: Session, supplier_id: int, amount: int = 1, description: str = "lead_purchase"):

    supplier = db.query(Supplier).get(supplier_id)

    if not supplier:
        return {"error": "supplier_not_found"}

    if supplier.credit < amount:
        return {"error": "insufficient_credit"}

    supplier.credit -= amount

    tx = CreditTransaction(
        supplier_id=supplier_id,
        amount=-amount,
        description=description
    )

    db.add(tx)
    db.commit()

    return {"success": True}


def add_credit(db: Session, supplier_id: int, amount: int, description: str = "manual_topup"):

    supplier = db.query(Supplier).get(supplier_id)

    if not supplier:
        return {"error": "supplier_not_found"}

    supplier.credit += amount

    tx = CreditTransaction(
        supplier_id=supplier_id,
        amount=amount,
        description=description
    )

    db.add(tx)
    db.commit()

    return {"success": True}
