from datetime import datetime

from services.redis_client import r


# =========================================================
# CONFIG
# =========================================================

OTP_KEY_PREFIX = "lae:otp:"


def _otp_key(
    phone: str,
) -> str:
    return f"{OTP_KEY_PREFIX}{phone}"


# =========================================================
# SAVE
# =========================================================

def save_otp(
    phone: str,
    code: str,
    expires_at: datetime,
):
    key = _otp_key(phone)

    now = datetime.utcnow()

    ttl = int(
        (
            expires_at - now
        ).total_seconds()
    )

    if ttl <= 0:
        ttl = 1

    pipe = r.pipeline()

    pipe.hset(
        key,
        mapping={
            "phone": phone,
            "code": str(code),
            "expires_at": expires_at.isoformat(),
            "created_at": now.isoformat(),
            "attempts": "0",
        },
    )

    pipe.expire(
        key,
        ttl,
    )

    pipe.execute()


# =========================================================
# GET
# =========================================================

def get_otp(
    phone: str,
):
    key = _otp_key(phone)

    item = r.hgetall(key)

    if not item:
        return None

    try:
        expires_at = datetime.fromisoformat(
            item["expires_at"]
        )

        created_at = datetime.fromisoformat(
            item["created_at"]
        )

        attempts = int(
            item.get(
                "attempts",
                0,
            )
        )

    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        delete_otp(phone)
        return None

    return {
        "phone": item.get(
            "phone",
            phone,
        ),
        "code": item.get(
            "code",
            "",
        ),
        "expires_at": expires_at,
        "created_at": created_at,
        "attempts": attempts,
    }


# =========================================================
# DELETE
# =========================================================

def delete_otp(
    phone: str,
):
    r.delete(
        _otp_key(phone)
    )


# =========================================================
# ATTEMPTS
# =========================================================

def increment_attempt(
    phone: str,
):
    key = _otp_key(phone)

    if not r.exists(key):
        return

    r.hincrby(
        key,
        "attempts",
        1,
    )


# =========================================================
# CLEANUP
# =========================================================

def cleanup_expired():
    # Redis removes expired OTP keys automatically.
    # This function remains for compatibility with otp.service.
    return 0