from fastapi import APIRouter

from otp.service import (
    send_otp,
    verify_otp
)

router = APIRouter(

    prefix="/otp",

    tags=["otp"]
)


@router.post(
    "/send"
)
def otp_send(

    payload: dict
):

    phone = payload.get(
        "phone"
    )

    if not phone:

        return {

            "success": False,

            "error":
                "phone_required"
        }

    return send_otp(
        phone
    )


@router.post(
    "/verify"
)
def otp_verify(

    payload: dict
):

    phone = payload.get(
        "phone"
    )

    code = payload.get(
        "code"
    )

    if (

        not phone

        or

        not code
    ):

        return {

            "success": False,

            "error":
                "missing_fields"
        }

    return verify_otp(

        phone,

        code
    )