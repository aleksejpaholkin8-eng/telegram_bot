# bot.py — бот с интеграцией Groq (бесплатно, до 14 400 запросов/день)
import asyncio
import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI  # Groq API полностью совместим с OpenAI SDK

# Загружаем переменные из .env (для локального запуска)
load_dotenv()

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# --- Читаем переменные окружения ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден! Добавьте его в переменные окружения.")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY не найден! Добавьте его в переменные окружения.")

# --- Создаём клиент Groq (через OpenAI SDK) ---
# Groq использует тот же формат запросов, что и OpenAI,
# но с другим base_url и своим API-ключом
groq_client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"  # Адрес API Groq[reference:10]
)

# Системный промпт — задаёт поведение бота
SYSTEM_PROMPT = "Ты — полезный, дружелюбный и умный ассистент. Отвечай кратко, ясно и по делу на русском языке."

# --- Основная функция бота ---
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer(
            "Привет! Я умный бот на базе Groq. Задай мне любой вопрос, и я постараюсь ответить."
        )

    @dp.message()
    async def handle_message(message: types.Message):
        if not message.text:
            await message.answer("Пожалуйста, отправьте текстовое сообщение.")
            return

        waiting_msg = await message.answer("🤔 Думаю...")

        try:
            # --- Запрос к Groq API ---
            # Используем модель llama-3.3-70b-versatile — быстрая и бесплатная[reference:11]
            # Можно заменить на "mixtral-8x7b-32768" или "gemma2-9b-it"
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message.text}
                ],
                max_tokens=500,
                temperature=0.7
            )

            answer = response.choices[0].message.content.strip()

            await waiting_msg.delete()
            await message.answer(answer)

        except Exception as e:
            await waiting_msg.delete()
            await message.answer(f"❌ Произошла ошибка при обращении к Groq: {e}")

    logging.info("Бот запускается и ждёт сообщения...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен вручную")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
