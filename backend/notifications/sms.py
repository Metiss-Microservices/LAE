import requests

from config import (
    SMS_API_KEY,
    SMS_SENDER
)


def send_sms(
    phone: str,
    text: str
) -> bool:

    if not SMS_API_KEY:
        return False

    try:

        r = requests.post(

            "https://api.sms.ir/v1/send",

            json={

                "mobile": phone,

                "message": text,

                "sender": SMS_SENDER
            },

            headers={
                "X-API-KEY": SMS_API_KEY
            },

            timeout=10
        )

        return r.status_code in [200, 201]

    except Exception:
        return False