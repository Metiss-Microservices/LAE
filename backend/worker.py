from time import sleep

from database import SessionLocal

from wallet.monthly_grants import (
    run_monthly_grants
)

from services.auction_service import (
    auto_finalize_expired_auctions
)


# =========================================================
# AUCTION WORKER
# =========================================================

def run_auction_worker():

    db = SessionLocal()

    while True:

        try:

            auto_finalize_expired_auctions(
                db
            )

        except Exception as e:

            print(
                f"[auction_worker] {e}"
            )

            db.rollback()

        sleep(5)


# =========================================================
# MONTHLY GRANT WORKER
# =========================================================

def run_credit_worker():

    db = SessionLocal()

    while True:

        try:

            run_monthly_grants(
                db
            )

        except Exception as e:

            print(
                f"[credit_worker] {e}"
            )

            db.rollback()

        sleep(3600)


# =========================================================
# MAIN
# =========================================================

def start_workers():

    import threading

    auction_thread = threading.Thread(

        target=run_auction_worker,

        daemon=True
    )

    credit_thread = threading.Thread(

        target=run_credit_worker,

        daemon=True
    )

    auction_thread.start()

    credit_thread.start()

    print(
        "workers started"
    )

    while True:

        sleep(60)


if __name__ == "__main__":

    start_workers()