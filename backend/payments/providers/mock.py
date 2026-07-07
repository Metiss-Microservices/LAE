from uuid import uuid4


# =========================================================
# CREATE PAYMENT
# =========================================================

def create_payment(
    amount,
    description,
    callback_url,
    phone=None
):

    authority = str(
        uuid4()
    )

    return {

        "success": True,

        "authority":
            authority,

        "payment_url":
            f"{callback_url}?authority={authority}"
    }


# =========================================================
# VERIFY PAYMENT
# =========================================================

def verify_payment(
    authority,
    amount
):

    return {

        "success": True,

        "ref_id":
            f"MOCK-{authority[:8]}",

        "card_pan":
            "603799******1234",

        "fee":
            0,

        "payload": {

            "authority":
                authority,

            "amount":
                amount
        }
    }