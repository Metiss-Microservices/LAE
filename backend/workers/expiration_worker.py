import time

from datetime import datetime

from database import SessionLocal

from models import LeadMatch


def process_expired_matches():

    db = SessionLocal()

    try:

        expired = db.query(LeadMatch).filter(

            LeadMatch.status == "pending",

            LeadMatch.expires_at < datetime.utcnow()

        ).all()

        count = 0

        for row in expired:

            row.status = "expired"

            count += 1

        db.commit()

        if count:

            print(
                f"⌛ expired matches updated: {count}"
            )

    except Exception as e:

        db.rollback()

        print(
            f"❌ expiration worker error: {e}"
        )

    finally:

        db.close()


def run():

    print("🧠 expiration worker started")

    while True:

        process_expired_matches()

        time.sleep(2)


if __name__ == "__main__":

    run()
