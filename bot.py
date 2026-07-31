import asyncio
import os
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI

# Принудительно UTF-8 (очень помогает на многих хостингах)
os.environ["PYTHONIOENCODING"] = "utf-8"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not BOT_TOKEN:
     # Временный дебаг (потом можно убрать)
    print("Доступные переменные:")
    for k, v in os.environ.items():
        if any(x in k.upper() for x in ["BOT", "GROQ", "KEY", "TOKEN", "API"]):
            print(k, "=", v[:20] + "..." if v and len(v) > 20 else v)
    raise ValueError("BOT_TOKEN не найден!")
if not GROQ_API_KEY:
    # Временный дебаг (потом можно убрать)
    print("Доступные переменные:")
    for k, v in os.environ.items():
        if any(x in k.upper() for x in ["BOT", "GROQ", "KEY", "TOKEN", "API"]):
            print(k, "=", v[:20] + "..." if v and len(v) > 20 else v)
    raise ValueError("GROQ_API_KEY не найден!")

# Создаём клиент
groq_client = OpenAI(
    api_key=GROQ_API_KEY.strip(),  # .strip() убирает случайные пробелы/переносы
    base_url="https://api.groq.com/openai/v1"
)

SYSTEM_PROMPT = "Ты — полезный, дружелюбный и умный ассистент. Отвечай кратко, ясно и по делу на русском языке."

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer("Привет! Я бот на Groq. Задай вопрос.")

    @dp.message()
    async def handle_message(message: types.Message):
        if not message.text:
            await message.answer("Пришли текстовое сообщение.")
            return

        waiting_msg = await message.answer("Думаю...")

        try:
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
            await message.answer(f"Ошибка Groq: {type(e).__name__}: {e}")
            logging.exception("Ошибка при запросе к Groq")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
