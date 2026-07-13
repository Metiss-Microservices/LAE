from time import sleep

from database import SessionLocal
from services.auction_service import auto_finalize_expired_auctions
from wallet.monthly_grants import run_monthly_grants


# =========================================================
# AUCTION WORKER
# =========================================================

def run_auction_worker():
    while True:
        db = SessionLocal()

        try:
            auto_finalize_expired_auctions(db)
        except Exception as e:
            print(e)
            db.rollback()
        finally:
            db.close()

        sleep(5)


# =========================================================
# MONTHLY GRANT WORKER
# =========================================================

def run_credit_worker():
    while True:
        db = SessionLocal()

        try:
            run_monthly_grants(db)
        except Exception:
            db.rollback()
        finally:
            db.close()

        sleep(3600)


# =========================================================
# MAIN
# =========================================================

def start_workers():
    import threading

    auction_thread = threading.Thread(
        target=run_auction_worker,
        daemon=True,
    )

    credit_thread = threading.Thread(
        target=run_credit_worker,
        daemon=True,
    )

    auction_thread.start()
    credit_thread.start()

    print("workers started")

    while True:
        sleep(60)


if __name__ == "__main__":
    start_workers()