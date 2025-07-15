import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from datetime import datetime, timedelta

API_TOKEN = 'SEU_TOKEN_AQUI'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Remove qualquer webhook antes de começar
async def on_startup(dp):
    await bot.delete_webhook()

scheduled_messages = {}

@dp.message_handler(commands=['start'])
async def start_handler(msg: types.Message):
    await msg.answer("👋 Olá! Use /set para agendar uma mensagem.")

@dp.message_handler(commands=['set'])
async def set_handler(msg: types.Message):
    await msg.answer("Use o comando assim:\n/set 10 Olá grupo!")

@dp.message_handler(lambda msg: msg.text.startswith('/set '))
async def handle_schedule(msg: types.Message):
    try:
        parts = msg.text.split(maxsplit=2)
        minutes = int(parts[1])
        content = parts[2]
        chat_id = msg.chat.id

        now = datetime.now()
        send_time = now + timedelta(minutes=minutes)
        scheduled_messages[chat_id] = {'text': content, 'time': send_time}

        await msg.answer(f"✅ Mensagem agendada para {send_time.strftime('%H:%M:%S')}:\n\n{content}")
    except Exception as e:
        await msg.answer("❌ Erro ao agendar a mensagem. Use: /set <minutos> <mensagem>")

async def message_scheduler():
    while True:
        now = datetime.now()
        for chat_id, data in list(scheduled_messages.items()):
            if now >= data['time']:
                try:
                    await bot.send_message(chat_id, data['text'])
                    del scheduled_messages[chat_id]
                except Exception as e:
                    print(f"Erro ao enviar mensagem: {e}")
        await asyncio.sleep(5)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(message_scheduler())
    executor.start_polling(dp, on_startup=on_startup)
