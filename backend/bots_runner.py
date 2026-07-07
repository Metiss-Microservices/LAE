import time
import asyncio
import threading

from bots.telegram.bot import (
    start_telegram_bot
)

from bots.bale.bot import (
    start_bale_bot
)

from bots.rubika.bot import (
    start_rubika_bot
)


# =========================================================
# TELEGRAM
# =========================================================

def run_telegram():

    try:

        asyncio.run(
            start_telegram_bot()
        )

    except Exception as e:

        print(
            f"❌ telegram bot error: {e}"
        )


# =========================================================
# BALE
# =========================================================

def run_bale():

    try:

        asyncio.run(
            start_bale_bot()
        )

    except Exception as e:

        print(
            f"❌ bale bot error: {e}"
        )


# =========================================================
# RUBIKA
# =========================================================

def run_rubika():

    try:

        asyncio.run(
            start_rubika_bot()
        )

    except Exception as e:

        print(
            f"❌ rubika bot error: {e}"
        )


# =========================================================
# START ALL
# =========================================================

def start_all_bots():

    bots = [

        (
            "telegram",
            run_telegram
        ),

        (
            "bale",
            run_bale
        ),

        (
            "rubika",
            run_rubika
        )
    ]

    for name, target in bots:

        thread = threading.Thread(

            target=target,

            daemon=True,

            name=name
        )

        thread.start()

        print(
            f"✅ {name} bot started"
        )

    print(
        "🤖 all bots online"
    )


if __name__ == "__main__":

    start_all_bots()

    try:

        while True:

            time.sleep(60)

    except KeyboardInterrupt:

        print(
            "🛑 bot runner shutdown"
        )