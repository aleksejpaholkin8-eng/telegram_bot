# bot.py — главный файл бота
import asyncio
import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Загружаем переменные из файла .env (локально) — на Railway они будут из настроек
load_dotenv()

# Включаем логирование, чтобы видеть события
logging.basicConfig(level=logging.INFO)

# Берём токен из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден! Добавьте его в переменные окружения.")

# Основная функция
async def main():
    # Создаём объект бота
    bot = Bot(token=BOT_TOKEN)

    # Диспетчер — обрабатывает сообщения
    dp = Dispatcher()

    # Обработчик команды /start
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer("Привет! Я бот-эхо. Отправь мне текст, и я отвечу тем же.")

    # Обработчик любого текстового сообщения
    @dp.message()
    async def echo(message: types.Message):
        if message.text:
            await message.answer(f"Вы сказали: {message.text}")
        else:
            await message.answer("Я понимаю только текст.")

    # Удаляем старые вебхуки, чтобы не было конфликтов
    await bot.delete_webhook(drop_pending_updates=True)

    logging.info("Бот запущен и ждёт сообщения...")

    # Запускаем бесконечный цикл опроса Telegram
    await dp.start_polling(bot)

# Точка входа
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен вручную")