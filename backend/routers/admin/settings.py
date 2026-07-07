from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from database import get_db

router = APIRouter(
    prefix="/admin/settings",
    tags=["admin-settings"]
)


SYSTEM_SETTINGS = {

    "race_timeout_seconds": 120,

    "claim_credit_cost": 1,

    "monthly_free_credit": 10,

    "auction_enabled": True,

    "notifications_enabled": True
}


@router.get("")
def get_settings(
    db: Session = Depends(get_db)
):

    return {
        "success": True,

        "settings":
            SYSTEM_SETTINGS
    }


@router.post("")
def update_settings(
    payload: dict
):

    for k, v in payload.items():

        if k in SYSTEM_SETTINGS:

            SYSTEM_SETTINGS[k] = v

    return {
        "success": True,

        "settings":
            SYSTEM_SETTINGS
    }
