# services/output_service.py

from sqlalchemy.orm import Session

import models


# =========================================================
# LOCATION NAME
# =========================================================

def get_location_name(
    db: Session,
    location_id
):

    if not location_id:
        return "-"

    loc = db.query(
        models.Location
    ).filter_by(
        id=location_id
    ).first()

    if not loc:
        return "-"

    names = []

    while loc:

        names.append(
            loc.name
        )

        if not loc.parent_id:
            break

        loc = db.query(
            models.Location
        ).filter_by(
            id=loc.parent_id
        ).first()

    names.reverse()

    return " / ".join(names)


# =========================================================
# SUPPLIER OUTPUT
# =========================================================

def build_supplier_output(
    db,
    match
):

    supplier = db.query(
        models.Supplier
    ).filter_by(
        id=match.supplier_id
    ).first()

    if not supplier:
        return None

    return {

        "match_id":
            str(match.id),

        "supplier_id":
            str(supplier.id),

        "supplier_name":
            supplier.full_name,

        "score":
            match.final_score,

        "base_score":
            match.base_score,

        "status":
            match.status,

        "wins":
            supplier.wins,

        "rating":
            supplier.score,

        "verified":
            supplier.is_verified,

        "bid_price":
            match.bid_price,

        "location":
            get_location_name(
                db,
                supplier.location_id
            )
    }


# =========================================================
# WINNER
# =========================================================

def get_winner(
    suppliers
):

    for item in suppliers:

        if item["status"] == "won":

            return item

    return None


# =========================================================
# BUILD OUTPUT
# =========================================================

def build_output(

    db: Session,

    lead_id,

    strategy="best"
):

    lead = db.query(
        models.Lead
    ).filter_by(
        id=lead_id
    ).first()

    if not lead:

        return {

            "success": False,

            "error":
                "lead_not_found"
        }

    matches = db.query(
        models.LeadMatch
    ).filter_by(
        lead_id=lead.id
    ).order_by(
        models.LeadMatch.final_score.desc()
    ).all()

    category = db.query(
        models.Category
    ).filter_by(
        id=lead.category_id
    ).first()

    subcategory = db.query(
        models.SubCategory
    ).filter_by(
        id=lead.subcategory_id
    ).first()

    suppliers = []

    for match in matches:

        item = build_supplier_output(
            db,
            match
        )

        if item:
            suppliers.append(
                item
            )

    winner = get_winner(
        suppliers
    )

    return {

        "success": True,

        "lead": {

            "id":
                str(lead.id),

            "client_id":
                str(lead.client_id),

            "status":
                lead.status,

            "priority_mode":
                lead.priority_mode,

            "category":
                category.name
                if category
                else "-",

            "subcategory":
                subcategory.name
                if subcategory
                else "-",

            "problem":
                lead.problem,

            "location":
                get_location_name(
                    db,
                    lead.location_id
                )
        },

        "winner":
            winner,

        "supplier_count":
            len(suppliers),

        "suppliers":
            suppliers
    }


# =========================================================
# LEAD SUMMARY
# =========================================================

def lead_summary(
    db,
    lead_id
):

    output = build_output(
        db,
        lead_id
    )

    if not output.get(
        "success"
    ):
        return output

    return {

        "lead_id":
            output["lead"]["id"],

        "status":
            output["lead"]["status"],

        "priority_mode":
            output["lead"]["priority_mode"],

        "supplier_count":
            output["supplier_count"],

        "winner":
            output["winner"]
    }


# =========================================================
# WINNER CONTACT
# =========================================================

def winner_contact(
    db,
    lead_id
):

    winner_match = db.query(
        models.LeadMatch
    ).filter_by(
        lead_id=lead_id,
        status="won"
    ).first()

    if not winner_match:
        return None

    supplier = db.query(
        models.Supplier
    ).filter_by(
        id=winner_match.supplier_id
    ).first()

    if not supplier:
        return None

    return {

        "supplier_id":
            str(supplier.id),

        "name":
            supplier.full_name,

        "phone":
            supplier.phone
    }