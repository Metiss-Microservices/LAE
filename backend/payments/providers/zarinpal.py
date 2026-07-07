import requests

from config import (
    ZARINPAL_MERCHANT_ID,
    ZARINPAL_SANDBOX
)


# =========================================================
# URLS
# =========================================================

if ZARINPAL_SANDBOX:

    REQUEST_URL = (
        "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
    )

    VERIFY_URL = (
        "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
    )

    START_URL = (
        "https://sandbox.zarinpal.com/pg/StartPay/"
    )

else:

    REQUEST_URL = (
        "https://api.zarinpal.com/pg/v4/payment/request.json"
    )

    VERIFY_URL = (
        "https://api.zarinpal.com/pg/v4/payment/verify.json"
    )

    START_URL = (
        "https://www.zarinpal.com/pg/StartPay/"
    )


# =========================================================
# CREATE PAYMENT
# =========================================================

def create_payment(
    amount,
    description,
    callback_url,
    phone=None
):

    try:

        payload = {

            "merchant_id":
                ZARINPAL_MERCHANT_ID,

            "amount":
                int(amount),

            "description":
                description,

            "callback_url":
                callback_url
        }

        if phone:

            payload["metadata"] = {
                "mobile": phone
            }

        response = requests.post(

            REQUEST_URL,

            json=payload,

            timeout=20
        )

        data = response.json()

        result = data.get(
            "data",
            {}
        )

        authority = result.get(
            "authority"
        )

        if not authority:

            return {
                "success": False,
                "error": "authority_not_received",
                "payload": data
            }

        return {

            "success": True,

            "authority":
                authority,

            "payment_url":
                f"{START_URL}{authority}"
        }

    except Exception as e:

        return {

            "success": False,

            "error":
                str(e)
        }


# =========================================================
# VERIFY PAYMENT
# =========================================================

def verify_payment(
    authority,
    amount
):

    try:

        payload = {

            "merchant_id":
                ZARINPAL_MERCHANT_ID,

            "authority":
                authority,

            "amount":
                int(amount)
        }

        response = requests.post(

            VERIFY_URL,

            json=payload,

            timeout=20
        )

        data = response.json()

        result = data.get(
            "data",
            {}
        )

        ref_id = result.get(
            "ref_id"
        )

        if not ref_id:

            return {

                "success": False,

                "payload":
                    data
            }

        return {

            "success": True,

            "ref_id":
                str(ref_id),

            "card_pan":
                result.get(
                    "card_pan"
                ),

            "fee":
                result.get(
                    "fee",
                    0
                ),

            "payload":
                data
        }

    except Exception as e:

        return {

            "success": False,

            "error":
                str(e)
        }