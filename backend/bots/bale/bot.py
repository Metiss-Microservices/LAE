from config import BALE_BOT_TOKEN

from bots.bale.handlers import (
    handle_bale_message
)


async def start_bale_bot():

    if not BALE_BOT_TOKEN:

        print(
            "bale token missing"
        )

        return

    print(
        "bale bot started"
    )

    #
    # TODO:
    # Bale SDK polling/webhook
    #

    while True:
        pass


async def bale_message_received(
    message
):

    await handle_bale_message(
        message
    )