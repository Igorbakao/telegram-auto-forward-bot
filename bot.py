import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from config import API_TOKEN

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

scheduled_messages = {}

@dp.message(F.text == "/start")
async def start_handler(msg: Message):
    await msg.answer("👋 Olá! Use /set para agendar uma mensagem.")

@dp.message(F.text.startswith("/set "))
async def handle_schedule(msg: Message):
    try:
        parts = msg.text.split(maxsplit=2)
        minutes = int(parts[1])
        content = parts[2]
        chat_id = msg.chat.id

        send_time = datetime.now() + timedelta(minutes=minutes)
        scheduled_messages[chat_id] = {"text": content, "time": send_time}

        await msg.answer(f"✅ Mensagem agendada para {send_time.strftime('%H:%M:%S')}:

{content}")
    except Exception as e:
        await msg.answer("❌ Erro ao agendar. Use: /set <minutos> <mensagem>")

async def message_scheduler():
    while True:
        now = datetime.now()
        for chat_id, data in list(scheduled_messages.items()):
            if now >= data["time"]:
                try:
                    await bot.send_message(chat_id, data["text"])
                    del scheduled_messages[chat_id]
                except Exception as e:
                    print(f"Erro ao enviar mensagem: {e}")
        await asyncio.sleep(5)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)  # remove webhook ativo
    asyncio.create_task(message_scheduler())             # inicia o agendador
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
