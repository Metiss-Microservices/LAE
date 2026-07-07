import requests


CREATE_URL = "https://api.idpay.ir/v1.1/payment"

VERIFY_URL = "https://api.idpay.ir/v1.1/payment/verify"


# =========================================================
# create payment
# =========================================================

def create_payment(
    api_key,
    amount,
    order_id,
    phone,
    callback
):

    headers = {

        "X-API-KEY": api_key,

        "Content-Type":
            "application/json"
    }

    payload = {

        "order_id":
            order_id,

        "amount":
            amount,

        "phone":
            phone,

        "callback":
            callback
    }

    try:

        r = requests.post(

            CREATE_URL,

            headers=headers,

            json=payload,

            timeout=20
        )

        if r.status_code not in [200, 201]:

            return {
                "success": False
            }

        data = r.json()

        return {

            "success": True,

            "data": data
        }

    except Exception:

        return {
            "success": False
        }


# =========================================================
# verify payment
# =========================================================

def verify_payment(
    api_key,
    id_,
    order_id
):

    headers = {

        "X-API-KEY": api_key,

        "Content-Type":
            "application/json"
    }

    payload = {

        "id": id_,

        "order_id":
            order_id
    }

    try:

        r = requests.post(

            VERIFY_URL,

            headers=headers,

            json=payload,

            timeout=20
        )

        if r.status_code != 200:

            return {
                "success": False
            }

        data = r.json()

        return {

            "success":
                data.get("status") == 100
        }

    except Exception:

        return {
            "success": False
        }