from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from database import get_db

from identity.dependencies import (
    admin_required
)

from models import (
    Supplier
)

router = APIRouter(
    prefix="/admin/channels",
    tags=["admin-channels"]
)


# =========================================================
# CHANNEL STATS
# =========================================================

@router.get("/stats")
def channel_stats(
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    telegram = db.query(
        Supplier
    ).filter(
        Supplier.telegram_chat_id.isnot(None)
    ).count()

    bale = db.query(
        Supplier
    ).filter(
        Supplier.bale_chat_id.isnot(None)
    ).count()

    rubika = db.query(
        Supplier
    ).filter(
        Supplier.rubika_chat_id.isnot(None)
    ).count()

    return {

        "success": True,

        "telegram":
            telegram,

        "bale":
            bale,

        "rubika":
            rubika
    }


# =========================================================
# CONNECTED USERS
# =========================================================

@router.get("/connected")
def connected_accounts(
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    rows = db.query(
        Supplier
    ).all()

    return {

        "success": True,

        "items": [

            {

                "supplier_id":
                    str(x.id),

                "full_name":
                    x.full_name,

                "telegram":
                    bool(
                        x.telegram_chat_id
                    ),

                "bale":
                    bool(
                        x.bale_chat_id
                    ),

                "rubika":
                    bool(
                        x.rubika_chat_id
                    )
            }

            for x in rows
        ]
    }


# =========================================================
# CHANNEL HEALTH
# =========================================================

@router.get("/health")
def channel_health(
    admin=Depends(admin_required)
):

    return {

        "success": True,

        "telegram":
            "online",

        "bale":
            "online",

        "rubika":
            "online"
    }
