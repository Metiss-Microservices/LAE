from database import SessionLocal

from identity.session import (
    get_session_by_token
)

from models import Supplier
from models import Client

from bots.telegram.supplier_flow import (
    supplier_menu,
    supplier_profile,
    supplier_wallet,
    supplier_credits,
    supplier_wins,
    supplier_open_leads
)

from bots.telegram.client_flow import (
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
        telegram_chat_id=str(chat_id)
    ).first()


def get_client_by_chat(
    db,
    chat_id
):

    return db.query(
        Client
    ).filter_by(
        telegram_chat_id=str(chat_id)
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

                supplier.telegram_chat_id = str(
                    chat_id
                )

        elif session.user_type == "client":

            client = db.query(
                Client
            ).filter_by(
                id=session.user_id
            ).first()

            if client:

                client.telegram_chat_id = str(
                    chat_id
                )

        db.commit()

        return True

    finally:

        db.close()


async def handle_telegram_message(
    message
):

    text = (
        message.text or ""
    ).strip()

    chat_id = str(
        message.chat.id
    )

    # --------------------------------
    # CONNECT
    # --------------------------------

    if text.startswith(
        "/connect"
    ):

        parts = text.split()

        if len(parts) != 2:

            await message.answer(
                "usage:\n/connect TOKEN"
            )

            return

        ok = await connect_account(
            parts[1],
            chat_id
        )

        if ok:

            await message.answer(
                "✅ connected"
            )

        else:

            await message.answer(
                "invalid token"
            )

        return

    db = SessionLocal()

    try:

        supplier = get_supplier_by_chat(
            db,
            chat_id
        )

        if supplier:

            if text == "/menu":

                await message.answer(
                    supplier_menu()
                )

                return

            if text == "/profile":

                await message.answer(
                    supplier_profile(
                        supplier.id
                    )
                )

                return

            if text == "/wallet":

                await message.answer(
                    supplier_wallet(
                        supplier.id
                    )
                )

                return

            if text == "/credits":

                await message.answer(
                    supplier_credits(
                        supplier.id
                    )
                )

                return

            if text == "/wins":

                await message.answer(
                    supplier_wins(
                        supplier.id
                    )
                )

                return

            if text == "/openleads":

                await message.answer(
                    supplier_open_leads(
                        supplier.id
                    )
                )

                return

        client = get_client_by_chat(
            db,
            chat_id
        )

        if client:

            if text == "/menu":

                await message.answer(
                    client_menu()
                )

                return

            if text == "/profile":

                await message.answer(
                    client_profile(
                        client.id
                    )
                )

                return

            if text == "/requests":

                await message.answer(
                    client_requests(
                        client.id
                    )
                )

                return

        await message.answer(
            "unknown command"
        )

    finally:

        db.close()