# notifications/templates.py

# =========================================================
# NEW LEAD
# =========================================================

def build_new_lead_message(
    lead,
    match_score=None,
    category=None,
    city=None
):

    return (
        f"🔥 لید جدید\n\n"
        f"دسته: {category or '-'}\n"
        f"شهر: {city or '-'}\n\n"
        f"{lead.problem or '-'}\n\n"
        f"امتیاز مچ: {match_score or 0}\n\n"
        f"برای ورود به Race اقدام کنید."
    )


# =========================================================
# RACE OPEN
# =========================================================

def build_race_open_message(
    lead_id,
    expires_in
):

    return (
        f"⚡ Race فعال شد\n\n"
        f"Lead: {lead_id}\n"
        f"مهلت: {expires_in} ثانیه\n\n"
        f"برای Claim وارد Race شوید."
    )


# =========================================================
# CLAIM WON
# =========================================================

def build_claim_won_message(
    lead,
    client_name=None
):

    return (
        f"🏆 شما برنده لید شدید\n\n"
        f"{lead.problem or '-'}\n\n"
        f"مشتری: {client_name or '-'}\n\n"
        f"اکنون می‌توانید اطلاعات تماس را مشاهده کنید."
    )


# =========================================================
# CLAIM LOST
# =========================================================

def build_claim_lost_message(
    lead
):

    return (
        f"❌ این لید توسط تامین‌کننده دیگری Claim شد\n\n"
        f"{lead.problem or '-'}"
    )


# =========================================================
# CONTACT UNLOCKED
# =========================================================

def build_contact_unlocked_message(
    customer_name,
    customer_phone
):

    return (
        f"📞 اطلاعات مشتری آزاد شد\n\n"
        f"نام: {customer_name}\n"
        f"تلفن: {customer_phone}"
    )


# =========================================================
# WALLET CHARGED
# =========================================================

def build_wallet_charged_message(
    amount,
    balance
):

    return (
        f"💰 کیف پول شارژ شد\n\n"
        f"مبلغ: {amount:,}\n"
        f"موجودی جدید: {balance:,}"
    )


# =========================================================
# CREDIT PURCHASED
# =========================================================

def build_credit_purchase_message(
    credits,
    balance
):

    return (
        f"🎫 اعتبار خریداری شد\n\n"
        f"اعتبار اضافه شده: {credits}\n"
        f"موجودی اعتبار: {balance}"
    )


# =========================================================
# CREDIT CONSUMED
# =========================================================

def build_credit_consumed_message(
    amount,
    balance
):

    return (
        f"🎯 اعتبار مصرف شد\n\n"
        f"مصرف شده: {amount}\n"
        f"مانده اعتبار: {balance}"
    )


# =========================================================
# MONTHLY GRANT
# =========================================================

def build_monthly_grant_message(
    amount,
    balance
):

    return (
        f"🎁 اعتبار ماهانه واریز شد\n\n"
        f"دریافتی: {amount}\n"
        f"موجودی اعتبار: {balance}"
    )


# =========================================================
# LOW CREDIT
# =========================================================

def build_low_credit_message(
    balance
):

    return (
        f"⚠️ اعتبار شما رو به اتمام است\n\n"
        f"موجودی فعلی: {balance}"
    )


# =========================================================
# LOW WALLET
# =========================================================

def build_low_wallet_message(
    balance
):

    return (
        f"⚠️ موجودی کیف پول کم است\n\n"
        f"موجودی فعلی: {balance:,}"
    )


# =========================================================
# SCORE UPDATE
# =========================================================

def build_score_update_message(
    score
):

    return (
        f"⭐ امتیاز شما بروزرسانی شد\n\n"
        f"امتیاز فعلی: {score}"
    )


# =========================================================
# REVIEW RECEIVED
# =========================================================

def build_review_received_message(
    rating,
    comment=None
):

    msg = (
        f"⭐ نظر جدید ثبت شد\n\n"
        f"امتیاز: {rating}"
    )

    if comment:
        msg += f"\n\n{comment}"

    return msg


# =========================================================
# SYSTEM
# =========================================================

def build_system_message(
    title,
    body
):

    return (
        f"🔔 {title}\n\n"
        f"{body}"
    )