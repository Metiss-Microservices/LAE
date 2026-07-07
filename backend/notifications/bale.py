import requests

from config import BALE_BOT_TOKEN


def send_bale_message(
    chat_id: str,
    text: str
) -> bool:

    if not BALE_BOT_TOKEN:
        return False

    try:

        r = requests.post(

            f"https://tapi.bale.ai/bot{BALE_BOT_TOKEN}/sendMessage",

            json={
                "chat_id": chat_id,
                "text": text
            },

            timeout=10
        )

        return r.status_code == 200

    except Exception:
        return False