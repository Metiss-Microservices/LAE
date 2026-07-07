from fastapi import Header
from fastapi import Depends

from sqlalchemy.orm import Session

from database import get_db

from identity.service import (
    get_supplier_by_token,
    get_client_by_token
)


def supplier_auth(

    token: str = Header(None),

    db: Session = Depends(get_db)
):

    return get_supplier_by_token(
        db,
        token
    )


def client_auth(

    token: str = Header(None),

    db: Session = Depends(get_db)
):

    return get_client_by_token(
        db,
        token
    )
