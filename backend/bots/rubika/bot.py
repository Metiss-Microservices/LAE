from config import RUBIKA_BOT_TOKEN

from bots.rubika.handlers import (
    handle_rubika_message
)


async def start_rubika_bot():

    if not RUBIKA_BOT_TOKEN:

        print(
            "rubika token missing"
        )

        return

    print(
        "rubika bot started"
    )

    #
    # TODO:
    # rubika webhook/polling
    #

    while True:
        pass


async def rubika_message_received(
    message
):

    await handle_rubika_message(
        message
    )