# backend/config.py

import os

# =========================================================

# PROJECT

# =========================================================

PROJECT_NAME = "LAE"

PROJECT_VERSION = "7.0.0"

ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    "production"
)

DEBUG = os.getenv(
    "DEBUG",
    "false"
).lower() == "true"

# =========================================================

# DATABASE

# =========================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@postgres:5432/lae"
)

REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://redis:6379/0"
)

# =========================================================

# MATCHING ENGINE

# =========================================================

MATCH_LIMIT = int(
    os.getenv(
        "MATCH_LIMIT",
        "5"
    )
)

DEFAULT_LEAD_TTL = int(
    os.getenv(
        "DEFAULT_LEAD_TTL",
        "300"
    )
)

WAVE2_TTL = int(
    os.getenv(
        "WAVE2_TTL",
        "60"
    )
)

RACE_LOCK_SECONDS = int(
    os.getenv(
        "RACE_LOCK_SECONDS",
        "15"
    )
)

# =========================================================
# PRICING (Backward Compatibility)
# =========================================================

PRICING = {
    "race_ttl": int(
        os.getenv(
            "RACE_TTL",
            "120"
        )
    )
}

# =========================================================

# PRIORITY MODES

# =========================================================

PRIORITY_MODES = [
    "smart",
    "nearest",
    "experienced",
    "fastest",
    "cheapest"
]

DEFAULT_PRIORITY_MODE = "smart"

# =========================================================

# CREDIT / WALLET

# =========================================================

MONTHLY_FREE_CREDITS = int(
    os.getenv(
        "MONTHLY_FREE_CREDITS",
        "50"
    )
)

DEFAULT_CLAIM_COST = int(
    os.getenv(
        "DEFAULT_CLAIM_COST",
        "1"
    )
)

# =========================================================

# OTP

# =========================================================

OTP_EXPIRE_SECONDS = int(
    os.getenv(
        "OTP_EXPIRE_SECONDS",
        "120"
    )
)

OTP_LENGTH = int(
    os.getenv(
        "OTP_LENGTH",
        "4"
    )
)

# =========================================================

# SESSION

# =========================================================

SESSION_EXPIRE_DAYS = int(
    os.getenv(
        "SESSION_EXPIRE_DAYS",
        "90"
    )
)

# =========================================================

# PAYMENT

# =========================================================

PAYMENT_PROVIDER = os.getenv(
    "PAYMENT_PROVIDER",
    "zarinpal"
)

ZARINPAL_MERCHANT = os.getenv(
    "ZARINPAL_MERCHANT",
    "sandbox"
)

PAYMENT_CALLBACK = os.getenv(
    "PAYMENT_CALLBACK",
    "http://localhost/api/v1/payment/callback"
)

# =========================================================

# TELEGRAM

# =========================================================

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    ""
)

# =========================================================

# BALE

# =========================================================

BALE_BOT_TOKEN = os.getenv(
    "BALE_BOT_TOKEN",
    ""
)

# =========================================================

# RUBIKA

# =========================================================

RUBIKA_BOT_TOKEN = os.getenv(
    "RUBIKA_BOT_TOKEN",
    ""
)

# =========================================================

# SMS

# =========================================================

SMS_API_KEY = os.getenv(
    "SMS_API_KEY",
    ""
)

SMS_SENDER = os.getenv(
    "SMS_SENDER",
    ""
)

# =========================================================

# NOTIFICATIONS

# =========================================================

ENABLE_SMS = os.getenv(
    "ENABLE_SMS",
    "true"
).lower() == "true"

ENABLE_TELEGRAM = os.getenv(
    "ENABLE_TELEGRAM",
    "true"
).lower() == "true"

ENABLE_BALE = os.getenv(
    "ENABLE_BALE",
    "true"
).lower() == "true"

ENABLE_RUBIKA = os.getenv(
    "ENABLE_RUBIKA",
    "true"
).lower() == "true"

# =========================================================

# BROADCAST

# =========================================================

BROADCAST_BATCH_SIZE = int(
    os.getenv(
        "BROADCAST_BATCH_SIZE",
        "100"
    )
)

# =========================================================

# ADMIN

# =========================================================

ADMIN_AUDIT_ENABLED = os.getenv(
    "ADMIN_AUDIT_ENABLED",
    "true"
).lower() == "true"

# =========================================================

# WEBSOCKET

# =========================================================

WS_HEARTBEAT_SECONDS = int(
    os.getenv(
        "WS_HEARTBEAT_SECONDS",
        "30"
    )
)
