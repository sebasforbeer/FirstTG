import asyncio
import logging
import sys
from os import getenv

# aiogram — основна бібліотека для роботи з Telegram Bot API
from aiogram import Bot, Dispatcher, html  # html — утиліти для безпечного форматування
from aiogram.client.default import DefaultBotProperties  # властивості за замовчуванням для бота
from aiogram.enums import ParseMode  # доступні режими парсингу розмітки (HTML/Markdown)
from aiogram.filters import CommandStart  # фільтр для команди /start
from aiogram.types import Message  # тип об'єкта вхідного повідомлення

# python-dotenv — підвантажує змінні середовища з .env
from dotenv import load_dotenv
load_dotenv()  # шукає .env у поточному каталозі й експортує значення у середовище

# Зчитуємо токен з оточення. Назва ключа має збігатися з тим, що у .env
TOKEN = getenv("BOT_TOKEN")

# Dispatcher — центральний компонент маршрутизації подій у aiogram v3.
# Усі обробники (handler-и) підключаються саме до диспетчера або до Router, який реєструється в диспетчері.
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Обробник для команди `/start`.

    Пояснення:
      - Декоратор @dp.message(CommandStart()) означає, що ця корутина буде викликана
        лише коли повідомлення містить команду /start.
      - message: Message — об'єкт з усією інформацією про вхідне повідомлення.
      - html.bold(...) — безпечне форматування імені користувача у жирний шрифт.
    """
    await message.answer(f"Привіт, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Універсальний echo-обробник для всіх інших повідомлень.

    Як працює:
      - За замовчуванням цей обробник спрацьовує на будь-який тип повідомлень
        (текст, фото, стікери, документи, голосові тощо).
      - Прагнемо надіслати точну копію вхідного повідомлення тим самим користувачам/у той самий чат.
      - Деякі типи об'єктів Telegram не підтримують send_copy, тому страхуємося try/except.
    """
    try:
        # Надсилаємо ідентичну копію отриманого повідомлення назад у той самий чат.
        # Перевага send_copy у тому, що він сам визначає правильний метод відправлення
        # (sendMessage, sendPhoto, sendDocument, ...), якщо тип підтримується.
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # Якщо тип повідомлення не підтримується для копіювання (наприклад, деякі "особливі" типи),
        # відправимо текстову відповідь замість копії.
        await message.answer("Гарна спроба!")


async def main() -> None:
    """
    Точка входу для асинхронного запуску бота.

    Кроки:
      1) Перевіряємо наявність токена (часта причина збоїв — порожній BOT_TOKEN).
      2) Створюємо екземпляр Bot з parse_mode=HTML (щоб працювало форматування).
      3) Запускаємо нескінченний цикл опитування (polling), який слухає нові оновлення від Telegram.
         - Поки процес працює, бот отримує і обробляє апдейти.
    """
    # 1) Перевірка, що токен підвантажено зі змінних середовища
    if not TOKEN:
        # Даємо читабельне пояснення у лог і завершуємо процес із кодом помилки
        logging.critical(
            "Не знайдено BOT_TOKEN у змінних середовища. "
            "Створіть файл .env і додайте рядок: BOT_TOKEN=ваш_токен"
        )
        sys.exit(1)

    # 2) Створюємо екземпляр бота.
    # DefaultBotProperties дозволяє задати властивості за замовчуванням:
    #   - parse_mode=HTML: тепер у всіх message.answer()/edit_message_text() HTML буде парситись.
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # 3) Запускаємо полінг (довге опитування) — простий спосіб отримувати апдейти без вебхуків.
    #    У продакшн-середовищі інколи обирають webhook, але для локалу/poc polling — найпростіший старт.
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Налаштовуємо базове логування. Рівень INFO зазвичай достатній,
    # stream=sys.stdout — журнал писатиметься у стандартний вивід (видно в консолі/докері).
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Запускаємо головну корутину подійного циклу:
    # asyncio.run забезпечує створення і закриття event loop.
    # Якщо натиснути Ctrl+C, aiogram коректно завершить полінг і сесії.
    asyncio.run(main())
