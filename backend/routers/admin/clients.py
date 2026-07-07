from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from database import get_db

from models import Client

router = APIRouter(
    prefix="/admin/clients",
    tags=["admin-clients"]
)


@router.get("")
def list_clients(
    limit: int = 100,
    db: Session = Depends(get_db)
):

    rows = (
        db.query(Client)
        .order_by(
            Client.id.desc()
        )
        .limit(limit)
        .all()
    )

    return {
        "success": True,

        "clients": [
            {
                "id": str(x.id),

                "full_name":
                    x.full_name,

                "phone":
                    x.phone,

                "created_at":
                    str(
                        x.created_at
                    )
                    if getattr(
                        x,
                        "created_at",
                        None
                    )
                    else None
            }

            for x in rows
        ]
    }


@router.get("/{client_id}")
def get_client(
    client_id: str,
    db: Session = Depends(get_db)
):

    row = db.query(
        Client
    ).filter_by(
        id=client_id
    ).first()

    if not row:

        return {
            "success": False,
            "error": "client_not_found"
        }

    return {
        "success": True,

        "client": {
            "id": str(row.id),

            "full_name":
                row.full_name,

            "phone":
                row.phone
        }
    }
