from datetime import datetime

from database import SessionLocal

import models


def run_expired_matches():

    db = SessionLocal()

    try:

        rows = db.query(
            models.LeadMatch
        ).filter(
            models.LeadMatch.status == "pending",
            models.LeadMatch.expires_at < datetime.utcnow()
        ).all()

        for row in rows:

            row.status = "expired"

        db.commit()

        print(
            f"⌛ expired matches: {len(rows)}"
        )

    except Exception as e:

        db.rollback()

        print(
            "expired worker error",
            e
        )

    finally:

        db.close()


if __name__ == "__main__":

    run_expired_matches()
