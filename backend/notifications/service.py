# notifications/service.py

from typing import Dict
from typing import Optional

from notifications.telegram import send_telegram_message
from notifications.bale import send_bale_message
from notifications.rubika import send_rubika_message
from notifications.sms import send_sms


# =========================================================
# CHANNEL HELPERS
# =========================================================

def _send_sms(phone: str, text: str) -> bool:

    try:
        send_sms(phone, text)
        return True
    except Exception:
        return False


def _send_telegram(chat_id: str, text: str) -> bool:

    try:
        send_telegram_message(chat_id, text)
        return True
    except Exception:
        return False


def _send_bale(chat_id: str, text: str) -> bool:

    try:
        send_bale_message(chat_id, text)
        return True
    except Exception:
        return False


def _send_rubika(chat_id: str, text: str) -> bool:

    try:
        send_rubika_message(chat_id, text)
        return True
    except Exception:
        return False


# =========================================================
# GENERIC DISPATCH
# =========================================================

def notify_supplier(
    supplier,
    title: str,
    body: str
) -> Dict:

    text = f"{title}\n\n{body}"

    result = {
        "sms": False,
        "telegram": False,
        "bale": False,
        "rubika": False
    }

    if getattr(supplier, "notify_sms", True):

        phone = getattr(
            supplier,
            "phone",
            None
        )

        if phone:
            result["sms"] = _send_sms(
                phone,
                text
            )

    if getattr(
        supplier,
        "notify_telegram",
        True
    ):

        chat_id = getattr(
            supplier,
            "telegram_chat_id",
            None
        )

        if chat_id:
            result["telegram"] = _send_telegram(
                chat_id,
                text
            )

    if getattr(
        supplier,
        "notify_bale",
        True
    ):

        chat_id = getattr(
            supplier,
            "bale_chat_id",
            None
        )

        if chat_id:
            result["bale"] = _send_bale(
                chat_id,
                text
            )

    if getattr(
        supplier,
        "notify_rubika",
        True
    ):

        chat_id = getattr(
            supplier,
            "rubika_chat_id",
            None
        )

        if chat_id:
            result["rubika"] = _send_rubika(
                chat_id,
                text
            )

    result["sent"] = any(
        result.values()
    )

    return result


# =========================================================
# LEAD CREATED
# =========================================================

def build_new_lead_message(
    lead,
    category_name: str,
    subcategory_name: str,
    location_name: str
):

    return {

        "title":
            "📢 لید جدید",

        "body":

            f"دسته: {category_name}\n"
            f"زیر دسته: {subcategory_name}\n"
            f"شهر: {location_name}\n"
            f"اولویت: {lead.priority_mode}\n\n"
            f"{lead.problem}"
    }


# =========================================================
# RACE STARTED
# =========================================================

def build_race_started_message(
    lead_id
):

    return {

        "title":
            "🏁 Race شروع شد",

        "body":

            f"برای لید {lead_id}\n"
            f"وارد Race شوید."
    }


# =========================================================
# CLAIM SUCCESS
# =========================================================

def build_claim_success_message(
    lead_id
):

    return {

        "title":
            "🏆 لید برنده شد",

        "body":

            f"Lead: {lead_id}\n\n"
            f"اطلاعات مشتری اکنون قابل مشاهده است."
    }


# =========================================================
# CLAIM LOST
# =========================================================

def build_claim_lost_message(
    lead_id
):

    return {

        "title":
            "❌ Race پایان یافت",

        "body":

            f"لید {lead_id}\n"
            f"توسط تامین‌کننده دیگری Claim شد."
    }


# =========================================================
# CREDIT LOW
# =========================================================

def build_low_credit_message(
    balance
):

    return {

        "title":
            "⚠️ اعتبار کم",

        "body":

            f"اعتبار باقی مانده: {balance}\n\n"
            f"برای ادامه دریافت لید، کیف پول را شارژ کرده و اعتبار خریداری کنید."
    }


# =========================================================
# WALLET CHARGED
# =========================================================

def build_wallet_charged_message(
    amount,
    balance
):

    return {

        "title":
            "💳 کیف پول شارژ شد",

        "body":

            f"مبلغ: {amount}\n"
            f"موجودی فعلی: {balance}"
    }


# =========================================================
# CREDIT PURCHASED
# =========================================================

def build_credit_purchased_message(
    amount,
    balance
):

    return {

        "title":
            "🎯 اعتبار خریداری شد",

        "body":

            f"اعتبار افزوده شده: {amount}\n"
            f"اعتبار فعلی: {balance}"
    }


# =========================================================
# MONTHLY GRANT
# =========================================================

def build_monthly_grant_message(
    amount
):

    return {

        "title":
            "🎁 اعتبار ماهانه",

        "body":

            f"{amount} اعتبار رایگان به حساب شما اضافه شد."
    }


# =========================================================
# PROFILE VERIFIED
# =========================================================

def build_verified_message():

    return {

        "title":
            "✅ حساب تایید شد",

        "body":
            "وضعیت تامین‌کننده شما تایید شد."
    }


# =========================================================
# SYSTEM
# =========================================================

def build_system_message(
    title: str,
    body: str
):

    return {

        "title": title,
        "body": body
    }