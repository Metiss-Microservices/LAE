from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import (
    Session,
    joinedload
)

from database import get_db

from models import (
    Supplier,
    SupplierCategory,
    SupplierLocation,
    LeadMatch,
    SupplierReview,
    CreditTransaction,
    WalletTransaction,
    Category,
    SubCategory,
    Location
)

router = APIRouter(
    prefix="/admin/suppliers",
    tags=["admin-suppliers"]
)


# =========================================================
# LIST
# =========================================================

@router.get("")
def list_suppliers(
    limit: int = 100,
    verified: bool | None = None,
    category_id: str | None = None,
    location_id: str | None = None,
    db: Session = Depends(get_db)
):

    query = db.query(
        Supplier
    )

    if verified is not None:

        query = query.filter(
            Supplier.is_verified == verified
        )

    if category_id:

        query = (
            query
            .join(
                SupplierCategory,
                SupplierCategory.supplier_id
                == Supplier.id
            )
            .filter(
                SupplierCategory.category_id
                == category_id
            )
        )

    if location_id:

        query = (
            query
            .join(
                SupplierLocation,
                SupplierLocation.supplier_id
                == Supplier.id
            )
            .filter(
                SupplierLocation.location_id
                == location_id
            )
        )

    rows = (
        query
        .options(
            joinedload(
                Supplier.categories
            ),
            joinedload(
                Supplier.locations
            )
        )
        .order_by(
            Supplier.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    return {

        "success": True,

        "suppliers": [

            {
                "id":
                    str(x.id),

                "full_name":
                    x.full_name,

                "phone":
                    x.phone,

                "score":
                    x.score,

                "credit_balance":
                    x.credit_balance,

                "wallet_balance":
                    x.wallet_balance,

                "verified":
                    x.is_verified,

                "active":
                    x.is_active,

                "blocked":
                    x.is_blocked,

                "category_count":
                    len(x.categories),

                "location_count":
                    len(x.locations)
            }

            for x in rows
        ]
    }


# =========================================================
# DETAILS
# =========================================================

@router.get("/{supplier_id}")
def supplier_details(
    supplier_id: str,
    db: Session = Depends(get_db)
):

    supplier = (
        db.query(
            Supplier
        )
        .options(
            joinedload(
                Supplier.categories
            ),
            joinedload(
                Supplier.locations
            )
        )
        .filter(
            Supplier.id == supplier_id
        )
        .first()
    )

    if not supplier:

        return {
            "success": False,
            "error": "supplier_not_found"
        }

    matches = db.query(
        LeadMatch
    ).filter(
        LeadMatch.supplier_id
        == supplier.id
    ).count()

    wins = db.query(
        LeadMatch
    ).filter(
        LeadMatch.supplier_id
        == supplier.id,
        LeadMatch.status == "won"
    ).count()

    reviews = db.query(
        SupplierReview
    ).filter(
        SupplierReview.supplier_id
        == supplier.id
    ).count()

    categories = []

    for item in supplier.categories:

        cat = db.query(
            Category
        ).filter(
            Category.id
            == item.category_id
        ).first()

        sub = None

        if item.subcategory_id:

            sub = db.query(
                SubCategory
            ).filter(
                SubCategory.id
                == item.subcategory_id
            ).first()

        categories.append({

            "category_id":
                str(item.category_id),

            "category":
                cat.name if cat else None,

            "subcategory_id":
                str(item.subcategory_id)
                if item.subcategory_id
                else None,

            "subcategory":
                sub.name if sub else None
        })

    locations = []

    for item in supplier.locations:

        loc = db.query(
            Location
        ).filter(
            Location.id
            == item.location_id
        ).first()

        locations.append({

            "location_id":
                str(item.location_id),

            "location":
                loc.name if loc else None
        })

    return {

        "success": True,

        "supplier": {

            "id":
                str(
                    supplier.id
                ),

            "full_name":
                supplier.full_name,

            "phone":
                supplier.phone,

            "score":
                supplier.score,

            "credit_balance":
                supplier.credit_balance,

            "wallet_balance":
                supplier.wallet_balance,

            "verified":
                supplier.is_verified,

            "active":
                supplier.is_active,

            "blocked":
                supplier.is_blocked,

            "wins":
                wins,

            "matches":
                matches,

            "reviews":
                reviews,

            "categories":
                categories,

            "locations":
                locations
        }
    }


# =========================================================
# VERIFY
# =========================================================

@router.post("/{supplier_id}/verify")
def verify_supplier(
    supplier_id: str,
    db: Session = Depends(get_db)
):

    supplier = db.query(
        Supplier
    ).filter(
        Supplier.id == supplier_id
    ).first()

    if not supplier:

        return {
            "success": False,
            "error": "supplier_not_found"
        }

    supplier.is_verified = True

    db.commit()

    return {
        "success": True
    }


# =========================================================
# UNVERIFY
# =========================================================

@router.post("/{supplier_id}/unverify")
def unverify_supplier(
    supplier_id: str,
    db: Session = Depends(get_db)
):

    supplier = db.query(
        Supplier
    ).filter(
        Supplier.id == supplier_id
    ).first()

    if not supplier:

        return {
            "success": False,
            "error": "supplier_not_found"
        }

    supplier.is_verified = False

    db.commit()

    return {
        "success": True
    }


# =========================================================
# CREDIT ADJUST
# =========================================================

@router.post("/{supplier_id}/credit")
def admin_adjust_credit(
    supplier_id: str,
    payload: dict,
    db: Session = Depends(get_db),
):
    supplier = (
        db.query(Supplier)
        .filter(
            Supplier.id == supplier_id
        )
        .with_for_update()
        .first()
    )

    if not supplier:
        return {
            "success": False,
            "error": "supplier_not_found",
        }

    try:
        amount = int(
            payload.get(
                "amount",
                0,
            )
        )
    except (
        TypeError,
        ValueError,
    ):
        return {
            "success": False,
            "error": "invalid_amount",
        }

    if amount == 0:
        return {
            "success": False,
            "error": "amount_cannot_be_zero",
        }

    new_balance = (
        int(supplier.credit_balance or 0)
        + amount
    )

    if new_balance < 0:
        return {
            "success": False,
            "error": "insufficient_credit",
        }

    description = payload.get(
        "description",
        "admin credit adjustment",
    )

    reference_id = payload.get(
        "reference_id",
    )

    supplier.credit_balance = new_balance

    tx = CreditTransaction(
        supplier_id=supplier.id,
        amount=amount,
        type="admin_adjustment",
        reference_id=reference_id,
        balance_after=new_balance,
        description=description,
    )

    try:
        db.add(tx)
        db.commit()
        db.refresh(tx)

    except Exception:
        db.rollback()
        raise

    return {
        "success": True,
        "transaction_id": str(tx.id),
        "amount": amount,
        "credit_balance": new_balance,
    }

# =========================================================
# WALLET ADJUST
# =========================================================

@router.post("/{supplier_id}/wallet")
def admin_adjust_wallet(
    supplier_id: str,
    payload: dict,
    db: Session = Depends(get_db),
):
    supplier = (
        db.query(Supplier)
        .filter(
            Supplier.id == supplier_id
        )
        .with_for_update()
        .first()
    )

    if not supplier:
        return {
            "success": False,
            "error": "supplier_not_found",
        }

    try:
        amount = float(
            payload.get(
                "amount",
                0,
            )
        )
    except (
        TypeError,
        ValueError,
    ):
        return {
            "success": False,
            "error": "invalid_amount",
        }

    if amount == 0:
        return {
            "success": False,
            "error": "amount_cannot_be_zero",
        }

    new_balance = (
        float(supplier.wallet_balance or 0)
        + amount
    )

    if new_balance < 0:
        return {
            "success": False,
            "error": "insufficient_wallet_balance",
        }

    description = payload.get(
        "description",
        "admin wallet adjustment",
    )

    reference_id = payload.get(
        "reference_id",
    )

    supplier.wallet_balance = new_balance

    tx = WalletTransaction(
        supplier_id=supplier.id,
        amount=amount,
        type="admin_adjustment",
        status="success",
        reference_id=reference_id,
        balance_after=new_balance,
        description=description,
    )

    try:
        db.add(tx)
        db.commit()
        db.refresh(tx)

    except Exception:
        db.rollback()
        raise

    return {
        "success": True,
        "transaction_id": str(tx.id),
        "amount": amount,
        "wallet_balance": new_balance,
    }

# =========================================================
# TOP SUPPLIERS
# =========================================================

@router.get("/reports/top")
def top_suppliers(
    limit: int = 20,
    db: Session = Depends(get_db)
):

    rows = (
        db.query(
            Supplier
        )
        .order_by(
            Supplier.score.desc()
        )
        .limit(limit)
        .all()
    )

    return {

        "success": True,

        "suppliers": [

            {
                "id":
                    str(x.id),

                "full_name":
                    x.full_name,

                "score":
                    x.score,

                "wins":
                    x.wins,

                "verified":
                    x.is_verified
            }

            for x in rows
        ]
    }


# =========================================================
# ENABLE / DISABLE
# =========================================================

@router.post("/{supplier_id}/disable")
def disable_supplier(
    supplier_id: str,
    db: Session = Depends(get_db)
):

    supplier = db.query(
        Supplier
    ).filter(
        Supplier.id == supplier_id
    ).first()

    if not supplier:

        return {
            "success": False,
            "error": "supplier_not_found"
        }

    supplier.is_active = False

    db.commit()

    return {
        "success": True
    }


@router.post("/{supplier_id}/enable")
def enable_supplier(
    supplier_id: str,
    db: Session = Depends(get_db)
):

    supplier = db.query(
        Supplier
    ).filter(
        Supplier.id == supplier_id
    ).first()

    if not supplier:

        return {
            "success": False,
            "error": "supplier_not_found"
        }

    supplier.is_active = True

    db.commit()

    return {
        "success": True
    }