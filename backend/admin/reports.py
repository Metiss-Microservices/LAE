from sqlalchemy import func

from models import (
    Supplier,
    Client,
    Lead,
    LeadMatch,
    PaymentTransaction
)


# =========================================================
# EXECUTIVE REPORT
# =========================================================

def build_executive_report(
    db
):

    supplier_count = db.query(
        Supplier
    ).count()

    client_count = db.query(
        Client
    ).count()

    lead_count = db.query(
        Lead
    ).count()

    match_count = db.query(
        LeadMatch
    ).count()

    paid_volume = (

        db.query(

            func.coalesce(

                func.sum(
                    PaymentTransaction.amount
                ),

                0
            )
        )

        .filter(
            PaymentTransaction.status == "paid"
        )

        .scalar()
    )

    return {

        "suppliers":
            supplier_count,

        "clients":
            client_count,

        "leads":
            lead_count,

        "matches":
            match_count,

        "paid_volume":
            paid_volume
    }


# =========================================================
# SUPPLIER REPORT
# =========================================================

def supplier_report(
    db,
    supplier_id
):

    wins = db.query(
        LeadMatch
    ).filter(
        LeadMatch.supplier_id == supplier_id,
        LeadMatch.status == "won"
    ).count()

    matches = db.query(
        LeadMatch
    ).filter(
        LeadMatch.supplier_id == supplier_id
    ).count()

    return {

        "supplier_id":
            str(supplier_id),

        "wins":
            wins,

        "matches":
            matches
    }


# =========================================================
# LEAD REPORT
# =========================================================

def lead_report(
    db,
    lead_id
):

    matches = db.query(
        LeadMatch
    ).filter(
        LeadMatch.lead_id == lead_id
    ).count()

    winners = db.query(
        LeadMatch
    ).filter(
        LeadMatch.lead_id == lead_id,
        LeadMatch.status == "won"
    ).count()

    return {

        "lead_id":
            str(lead_id),

        "matches":
            matches,

        "winners":
            winners
    }
