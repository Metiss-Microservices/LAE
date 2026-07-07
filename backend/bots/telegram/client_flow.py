from database import SessionLocal

from models import Client
from models import Lead


def client_menu():

    return (
        "📌 منوی مشتری\n\n"
        "/profile\n"
        "/requests\n"
        "/status\n"
        "/help"
    )


def client_profile(
    client_id
):

    db = SessionLocal()

    try:

        client = db.query(
            Client
        ).filter_by(
            id=client_id
        ).first()

        if not client:
            return "client_not_found"

        return (
            f"👤 {client.full_name}\n"
            f"📱 {client.phone}"
        )

    finally:

        db.close()


def client_requests(
    client_id
):

    db = SessionLocal()

    try:

        rows = db.query(
            Lead
        ).filter_by(
            client_id=client_id
        ).order_by(
            Lead.created_at.desc()
        ).limit(10).all()

        if not rows:
            return "درخواستی وجود ندارد"

        result = []

        for row in rows:

            result.append(
                f"{row.id} | {row.status}"
            )

        return "\n".join(result)

    finally:

        db.close()