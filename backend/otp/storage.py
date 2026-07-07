from datetime import datetime

#
# V7
# replace with redis later
#

_otp_store = {}


def save_otp(
    phone: str,
    code: str,
    expires_at: datetime
):

    _otp_store[phone] = {

        "phone": phone,

        "code": str(code),

        "expires_at": expires_at,

        "created_at": datetime.utcnow(),

        "attempts": 0
    }


def get_otp(
    phone: str
):

    return _otp_store.get(
        phone
    )


def delete_otp(
    phone: str
):

    _otp_store.pop(
        phone,
        None
    )


def increment_attempt(
    phone: str
):

    item = _otp_store.get(
        phone
    )

    if not item:
        return

    item["attempts"] += 1


def cleanup_expired():

    now = datetime.utcnow()

    expired = []

    for phone, item in _otp_store.items():

        if item["expires_at"] <= now:

            expired.append(
                phone
            )

    for phone in expired:

        _otp_store.pop(
            phone,
            None
        )