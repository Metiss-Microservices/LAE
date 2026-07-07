from sqlalchemy.orm import Session

from models import Lead


# =========================================================
# GET LEAD
# =========================================================

def get_lead(
    db: Session,
    lead_id
):

    return db.query(
        Lead
    ).filter_by(
        id=lead_id
    ).first()


# =========================================================
# UPDATE STATUS
# =========================================================

def update_lead_status(

    db: Session,

    lead_id,

    status
):

    lead = db.query(
        Lead
    ).filter_by(
        id=lead_id
    ).first()

    if not lead:
        return False

    lead.status = status

    db.commit()

    return True
