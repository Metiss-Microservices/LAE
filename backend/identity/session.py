import uuid

from datetime import datetime
from datetime import timedelta

from sqlalchemy.orm import Session

from models import UserSession

from config import SESSION_EXPIRE_DAYS


def create_session(db: Session, identity_id, role: str):
    token = str(uuid.uuid4())

    session = UserSession(
        identity_id=identity_id,
        role=role,
        token=token,
        expires_at=(
            datetime.utcnow()
            + timedelta(days=SESSION_EXPIRE_DAYS)
        )
    )

    db.add(session)
    db.commit()

    return token


def remove_session(db: Session, token: str):
    db.query(
        UserSession
    ).filter_by(
        token=token
    ).delete()

    db.commit()


def get_session(db: Session, token: str):
    return db.query(
        UserSession
    ).filter_by(
        token=token
    ).first()
