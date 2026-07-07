import requests

from config import TELEGRAM_BOT_TOKEN


def send_telegram_message(
    chat_id: str,
    text: str
) -> bool:

    if not TELEGRAM_BOT_TOKEN:
        return False

    try:

        r = requests.post(

            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",

            json={
                "chat_id": chat_id,
                "text": text
            },

            timeout=10
        )

        return r.status_code == 200

    except Exception:
        return False