import requests

from config import RUBIKA_BOT_TOKEN


def send_rubika_message(
    chat_id: str,
    text: str
) -> bool:

    if not RUBIKA_BOT_TOKEN:
        return False

    try:

        r = requests.post(

            f"https://messengerg2c56.iranlms.ir/v3/{RUBIKA_BOT_TOKEN}/sendMessage",

            json={
                "chat_id": chat_id,
                "text": text
            },

            timeout=10
        )

        return r.status_code == 200

    except Exception:
        return False