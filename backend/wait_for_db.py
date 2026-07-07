import time

from sqlalchemy import text

from database import engine


def wait_for_db():

    while True:

        try:

            with engine.connect() as conn:

                conn.execute(
                    text("SELECT 1")
                )

            print("✅ DB READY")

            break

        except Exception as e:

            print("⏳ waiting for db...", e)

            time.sleep(2)


if __name__ == "__main__":

    wait_for_db()
