# workers/notification_worker.py

import asyncio

from database import SessionLocal

import models

from services.notification_dispatcher import (
dispatch_new_lead
)

# =========================================================

# LOOP

# =========================================================

async def run():

print(
    "📨 notification worker started"
)

while True:

    db = SessionLocal()

    try:

        rows = db.query(
            models.Lead
        ).filter_by(
            notification_sent=False
        ).all()

        for lead in rows:

            try:

                await dispatch_new_lead(

                    db,

                    lead.id
                )

                lead.notification_sent = True

            except Exception as e:

                print(
                    f"notification error: {e}"
                )

        db.commit()

    except Exception as e:

        print(
            f"worker error: {e}"
        )

        db.rollback()

    finally:

        db.close()

    await asyncio.sleep(5)

# =========================================================

# ENTRY

# =========================================================

if **name** == "**main**":

asyncio.run(
    run()
)
