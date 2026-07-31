# bot.py — бот с интеграцией DeepSeek
import asyncio
import os
import logging
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI  # Библиотека OpenAI подходит и для DeepSeek

# Загружаем переменные из .env (для локального запуска)
load_dotenv()

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# --- Читаем переменные окружения ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден! Добавьте его в переменные окружения.")

DEEPSEEK_API_KEY = "sk-ваш_ключ"  # вставьте ваш реальный ключ

# --- Создаём клиент DeepSeek (через OpenAI SDK) ---
# DeepSeek API полностью совместим с OpenAI API, поэтому мы используем ту же библиотеку,
# но меняем base_url на адрес DeepSeek[reference:3]
deepseek_client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"  # Адрес API DeepSeek[reference:4]
)

# Системный промпт — задаёт поведение бота (можете изменить по своему вкусу)
SYSTEM_PROMPT = "Ты — полезный, дружелюбный и умный ассистент. Отвечай кратко, ясно и по делу на русском языке."

# --- Основная функция бота ---
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Обработчик команды /start
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer(
            "Привет! Я умный бот на базе DeepSeek. Задай мне любой вопрос, и я постараюсь ответить."
        )

    # Обработчик всех текстовых сообщений
    @dp.message()
    async def handle_message(message: types.Message):
        if not message.text:
            await message.answer("Пожалуйста, отправьте текстовое сообщение.")
            return

        # Отправляем сообщение «Думаю...», чтобы пользователь знал, что бот работает
        waiting_msg = await message.answer("🤔 Думаю...")

        try:
            # --- Запрос к DeepSeek API ---
            # Используем модель deepseek-v4-flash (быстрая и недорогая)[reference:5]
            # Модель deepseek-v4-pro — более мощная, но дороже[reference:6]
            response = deepseek_client.chat.completions.create(
                model="deepseek-v4-flash",  # Можно заменить на "deepseek-v4-pro"
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message.text}
                ],
                max_tokens=500,          # Максимальная длина ответа
                temperature=0.7           # Степень креативности (0 — строго, 1 — креативно)
            )

            # Извлекаем ответ из ответа API
            answer = response.choices[0].message.content.strip()

            # Удаляем сообщение «Думаю...» и отправляем ответ
            await waiting_msg.delete()
            await message.answer(answer)

        except Exception as e:
            # Если что-то пошло не так — сообщаем об ошибке
            await waiting_msg.delete()
            await message.answer(f"❌ Произошла ошибка при обращении к DeepSeek: {e}")

    logging.info("Бот запускается и ждёт сообщения...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

# --- Точка входа ---
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен вручную")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
