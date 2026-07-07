from database import SessionLocal

from models import Supplier
from models import LeadMatch


def supplier_menu():

    return (
        "📌 منوی تامین کننده\n\n"
        "/profile\n"
        "/wallet\n"
        "/credits\n"
        "/score\n"
        "/wins\n"
        "/newleads\n"
        "/openleads\n"
        "/wonleads\n"
        "/history\n"
        "/help"
    )


def supplier_profile(
    supplier_id
):

    db = SessionLocal()

    try:

        supplier = db.query(
            Supplier
        ).filter_by(
            id=supplier_id
        ).first()

        if not supplier:
            return "supplier_not_found"

        return (
            f"👤 {supplier.full_name}\n\n"
            f"⭐ Score: {supplier.score}\n"
            f"🏆 Wins: {supplier.total_wins}\n"
            f"📊 Reputation: {supplier.reputation_score}"
        )

    finally:

        db.close()


def supplier_wallet(
    supplier_id
):

    db = SessionLocal()

    try:

        supplier = db.query(
            Supplier
        ).filter_by(
            id=supplier_id
        ).first()

        if not supplier:
            return "supplier_not_found"

        return (
            f"💰 Wallet\n\n"
            f"{supplier.wallet_balance:,}"
        )

    finally:

        db.close()


def supplier_credits(
    supplier_id
):

    db = SessionLocal()

    try:

        supplier = db.query(
            Supplier
        ).filter_by(
            id=supplier_id
        ).first()

        if not supplier:
            return "supplier_not_found"

        return (
            f"🎫 Credits\n\n"
            f"{supplier.credit_balance}"
        )

    finally:

        db.close()


def supplier_wins(
    supplier_id
):

    db = SessionLocal()

    try:

        wins = db.query(
            LeadMatch
        ).filter_by(
            supplier_id=supplier_id,
            status="won"
        ).count()

        return (
            f"🏆 Total Wins: {wins}"
        )

    finally:

        db.close()