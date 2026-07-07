from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from database import get_db

from identity.dependencies import (
    admin_required
)

router = APIRouter(
    prefix="/admin/campaigns",
    tags=["admin-campaigns"]
)

_campaign_memory = []


# =========================================================
# CREATE CAMPAIGN
# =========================================================

@router.post("")
def create_campaign(
    payload: dict,
    admin=Depends(admin_required)
):

    item = {

        "id":
            len(_campaign_memory) + 1,

        "title":
            payload.get(
                "title"
            ),

        "message":
            payload.get(
                "message"
            ),

        "target":
            payload.get(
                "target",
                "all"
            ),

        "status":
            "draft",

        "created_at":
            datetime.utcnow()
    }

    _campaign_memory.append(
        item
    )

    return {

        "success": True,

        "campaign":
            item
    }


# =========================================================
# LIST
# =========================================================

@router.get("")
def list_campaigns(
    admin=Depends(admin_required)
):

    return {

        "success": True,

        "items":
            _campaign_memory
    }


# =========================================================
# ACTIVATE
# =========================================================

@router.post("/{campaign_id}/activate")
def activate_campaign(
    campaign_id: int,
    admin=Depends(admin_required)
):

    for item in _campaign_memory:

        if item["id"] == campaign_id:

            item["status"] = "active"

            item["activated_at"] = (
                datetime.utcnow()
            )

            return {

                "success": True
            }

    return {

        "success": False,

        "error":
            "campaign_not_found"
    }


# =========================================================
# STOP
# =========================================================

@router.post("/{campaign_id}/stop")
def stop_campaign(
    campaign_id: int,
    admin=Depends(admin_required)
):

    for item in _campaign_memory:

        if item["id"] == campaign_id:

            item["status"] = "stopped"

            return {

                "success": True
            }

    return {

        "success": False,

        "error":
            "campaign_not_found"
    }


# =========================================================
# DELETE
# =========================================================

@router.delete("/{campaign_id}")
def delete_campaign(
    campaign_id: int,
    admin=Depends(admin_required)
):

    global _campaign_memory

    before = len(
        _campaign_memory
    )

    _campaign_memory = [

        x
        for x in _campaign_memory
        if x["id"] != campaign_id
    ]

    return {

        "success":
            before != len(
                _campaign_memory
            )
    }


# =========================================================
# REPORT
# =========================================================

@router.get("/{campaign_id}/report")
def campaign_report(
    campaign_id: int,
    admin=Depends(admin_required)
):

    for item in _campaign_memory:

        if item["id"] == campaign_id:

            return {

                "success": True,

                "campaign_id":
                    campaign_id,

                "status":
                    item["status"],

                "delivered":
                    0,

                "opened":
                    0,

                "clicked":
                    0
            }

    return {

        "success": False,

        "error":
            "campaign_not_found"
    }
