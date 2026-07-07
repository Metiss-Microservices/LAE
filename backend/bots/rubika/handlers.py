from database import SessionLocal

from identity.session import (
    get_session_by_token
)

from models import Supplier
from models import Client

from bots.rubika.supplier_flow import (
    supplier_menu,
    supplier_profile,
    supplier_wallet,
    supplier_credits,
    supplier_wins
)

from bots.rubika.client_flow import (
    client_menu,
    client_profile,
    client_requests
)


def get_supplier_by_chat(
    db,
    chat_id
):

    return db.query(
        Supplier
    ).filter_by(
        rubika_chat_id=str(chat_id)
    ).first()


def get_client_by_chat(
    db,
    chat_id
):

    return db.query(
        Client
    ).filter_by(
        rubika_chat_id=str(chat_id)
    ).first()


async def connect_account(
    token,
    chat_id
):

    db = SessionLocal()

    try:

        session = get_session_by_token(
            db,
            token
        )

        if not session:
            return False

        if session.user_type == "supplier":

            supplier = db.query(
                Supplier
            ).filter_by(
                id=session.user_id
            ).first()

            if supplier:

                supplier.rubika_chat_id = str(
                    chat_id
                )

        elif session.user_type == "client":

            client = db.query(
                Client
            ).filter_by(
                id=session.user_id
            ).first()

            if client:

                client.rubika_chat_id = str(
                    chat_id
                )

        db.commit()

        return True

    finally:

        db.close()


async def handle_rubika_message(
    message
):

    text = (
        getattr(
            message,
            "text",
            ""
        ) or ""
    ).strip()

    chat_id = str(
        getattr(
            message,
            "chat_id",
            ""
        )
    )

    if text.startswith(
        "/connect"
    ):

        parts = text.split()

        if len(parts) != 2:

            return (
                "usage:\n/connect TOKEN"
            )

        ok = await connect_account(
            parts[1],
            chat_id
        )

        if ok:

            return "✅ connected"

        return "invalid token"

    db = SessionLocal()

    try:

        supplier = get_supplier_by_chat(
            db,
            chat_id
        )

        if supplier:

            if text == "/menu":
                return supplier_menu()

            if text == "/profile":
                return supplier_profile(
                    supplier.id
                )

            if text == "/wallet":
                return supplier_wallet(
                    supplier.id
                )

            if text == "/credits":
                return supplier_credits(
                    supplier.id
                )

            if text == "/wins":
                return supplier_wins(
                    supplier.id
                )

        client = get_client_by_chat(
            db,
            chat_id
        )

        if client:

            if text == "/menu":
                return client_menu()

            if text == "/profile":
                return client_profile(
                    client.id
                )

            if text == "/requests":
                return client_requests(
                    client.id
                )

        return "unknown command"

    finally:

        db.close()