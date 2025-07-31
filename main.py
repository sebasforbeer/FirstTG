import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from dotenv import load_dotenv
load_dotenv()

TOKEN = getenv("BOT_TOKEN")

# Всі обробники повинні бути підключені до маршрутизатора (або диспетчера)

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Цей обробник отримує повідомлення з командою `/start`.
    """
    await message.answer(f"Привіт, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Обробник перешле повідомлення назад відправнику

    За замовчуванням обробник повідомлень оброблятиме всі типи повідомлень (наприклад, текст, фото, стікери тощо).
    """
    try:
        # Надіслати копію отриманого повідомлення
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # Але не всі типи підтримуються для копіювання, тому потрібно це враховувати.
        await message.answer("Гарна спроба!")


async def main() -> None:
    #  Ініціалізуйте екземпляр бота з властивостями бота за замовчуванням, які будуть передані до всіх викликів API
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # І диспетчеризація подій запуску
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
