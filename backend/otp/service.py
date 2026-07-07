import random

from datetime import datetime
from datetime import timedelta

from config import OTP_LENGTH
from config import OTP_EXPIRE_SECONDS

from otp.storage import (
    save_otp,
    get_otp,
    delete_otp,
    increment_attempt,
    cleanup_expired
)

from notifications.sms import (
    send_sms
)


MAX_VERIFY_ATTEMPTS = 5


def generate_code():

    start = 10 ** (
        OTP_LENGTH - 1
    )

    end = (
        (10 ** OTP_LENGTH) - 1
    )

    return str(
        random.randint(
            start,
            end
        )
    )


def send_otp(
    phone: str
):

    cleanup_expired()

    code = generate_code()

    expires_at = (

        datetime.utcnow()

        +

        timedelta(
            seconds=
            OTP_EXPIRE_SECONDS
        )
    )

    save_otp(

        phone=phone,

        code=code,

        expires_at=expires_at
    )

    try:

        send_sms(

            phone,

            f"کد تایید شما: {code}"
        )

    except Exception as e:

        print(
            f"otp sms error: {e}"
        )

    return {

        "success": True,

        "expires_in":
            OTP_EXPIRE_SECONDS
    }


def verify_otp(

    phone: str,

    code: str
):

    cleanup_expired()

    item = get_otp(
        phone
    )

    if not item:

        return {

            "success": False,

            "error":
                "otp_not_found"
        }

    if (

        item["expires_at"]

        <

        datetime.utcnow()

    ):

        delete_otp(
            phone
        )

        return {

            "success": False,

            "error":
                "otp_expired"
        }

    if (

        item["attempts"]

        >=

        MAX_VERIFY_ATTEMPTS
    ):

        delete_otp(
            phone
        )

        return {

            "success": False,

            "error":
                "max_attempts"
        }

    if str(
        item["code"]
    ) != str(code):

        increment_attempt(
            phone
        )

        return {

            "success": False,

            "error":
                "invalid_code"
        }

    delete_otp(
        phone
    )

    return {

        "success": True
    }