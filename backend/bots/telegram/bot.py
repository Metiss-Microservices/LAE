from aiogram import Bot
from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart

from config import TELEGRAM_BOT_TOKEN

from bots.telegram.handlers import (
    handle_telegram_message
)

bot = Bot(
    token=TELEGRAM_BOT_TOKEN
)

dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(
    message: Message
):

    await message.answer(
        "🤖 LAE V7\n\n"
        "برای اتصال:\n"
        "/connect TOKEN"
    )


@dp.message()
async def generic_handler(
    message: Message
):

    await handle_telegram_message(
        message
    )


async def start_telegram_bot():

    if not TELEGRAM_BOT_TOKEN:

        print(
            "telegram token missing"
        )

        return

    print(
        "telegram bot started"
    )

    await dp.start_polling(bot)