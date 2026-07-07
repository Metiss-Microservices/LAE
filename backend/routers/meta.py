from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from database import get_db

import models

router = APIRouter(
    prefix="/meta",
    tags=["meta"]
)


# =========================================================
# CATEGORIES
# =========================================================

@router.get("/categories")
def get_categories(

    type: str = None,

    db: Session = Depends(get_db)
):

    query = db.query(
        models.Category
    )

    if type:

        query = query.filter(
            models.Category.type == type
        )

    rows = query.order_by(
        models.Category.name
    ).all()

    return {

        "success": True,

        "count": len(rows),

        "categories": [

            {

                "id":
                    str(row.id),

                "name":
                    row.name,

                "type":
                    row.type
            }

            for row in rows
        ]
    }


# =========================================================
# SUBCATEGORIES
# =========================================================

@router.get("/subcategories/{category_id}")
def get_subcategories(

    category_id: str,

    db: Session = Depends(get_db)
):

    rows = db.query(
        models.SubCategory
    ).filter_by(
        category_id=category_id
    ).order_by(
        models.SubCategory.name
    ).all()

    return {

        "success": True,

        "count": len(rows),

        "subcategories": [

            {

                "id":
                    str(row.id),

                "name":
                    row.name,

                "category_id":
                    str(row.category_id)
            }

            for row in rows
        ]
    }


# =========================================================
# LOCATIONS
# =========================================================

@router.get("/locations")
def get_locations(

    parent_id: str = None,

    db: Session = Depends(get_db)
):

    query = db.query(
        models.Location
    )

    if parent_id:

        query = query.filter(
            models.Location.parent_id
            == parent_id
        )

    rows = query.order_by(
        models.Location.name
    ).all()

    return {

        "success": True,

        "count": len(rows),

        "locations": [

            {

                "id":
                    str(row.id),

                "name":
                    row.name,

                "type":
                    row.type,

                "parent_id":
                    str(row.parent_id)
                    if row.parent_id
                    else None
            }

            for row in rows
        ]
    }


# =========================================================
# SUPPLIER CATEGORIES (V7)
# =========================================================

@router.get(
    "/supplier-categories/{supplier_id}"
)
def get_supplier_categories(

    supplier_id: str,

    db: Session = Depends(get_db)
):

    rows = db.query(
        models.SupplierCategory
    ).filter_by(
        supplier_id=supplier_id
    ).all()

    return {

        "success": True,

        "count": len(rows),

        "items": [

            {

                "category_id":
                    str(row.category_id),

                "subcategory_id":
                    str(row.subcategory_id)
                    if row.subcategory_id
                    else None
            }

            for row in rows
        ]
    }


# =========================================================
# PRIORITY MODES
# =========================================================

@router.get("/priority-modes")
def get_priority_modes():

    return {

        "success": True,

        "modes": [

            "smart",

            "fastest",

            "experienced",

            "cheapest"
        ]
    }


# =========================================================
# HEALTH
# =========================================================

@router.get("/health")
def health():

    return {

        "success": True,

        "service": "meta",

        "version": "v7"
    }