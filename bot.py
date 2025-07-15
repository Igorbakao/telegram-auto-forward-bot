import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

message_to_send = ""
send_interval = 60  # seconds
is_running = False
task = None  # for loop control

# Inline buttons
def control_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("▶ Start", callback_data="start"),
        InlineKeyboardButton("⏹ Stop", callback_data="stop")
    )
    return keyboard

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer(
        "Welcome! This bot sends a message automatically at the interval you choose.\n\nUse:\n- /add Your message\n- /interval Number (minutes)\n\nThen tap the buttons below:",
        reply_markup=control_keyboard()
    )

@dp.message_handler(commands=["add"])
async def add(msg: types.Message):
    global message_to_send
    text = msg.get_args()
    if not text:
        await msg.reply("Use the command like this:\n`/add Your message here`", parse_mode="Markdown")
    else:
        message_to_send = text
        await msg.reply(f"✅ Message set:\n\n{message_to_send}")

@dp.message_handler(commands=["interval"])
async def set_interval(msg: types.Message):
    global send_interval
    try:
        minutes = int(msg.get_args())
        send_interval = minutes * 60
        await msg.reply(f"✅ Interval set to {minutes} minutes.")
    except:
        await msg.reply("Use the command like this:\n`/interval 10`", parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data == "start")
async def start_sending(callback: types.CallbackQuery):
    global is_running, task
    if not message_to_send:
        await callback.answer("Please set a message first using /add.")
        return
    if is_running:
        await callback.answer("Already running.")
        return

    is_running = True
    await callback.answer("🚀 Started!")

    async def sending_loop():
        while is_running:
            await bot.send_message(callback.message.chat.id, message_to_send)
            await asyncio.sleep(send_interval)

    task = asyncio.create_task(sending_loop())

@dp.callback_query_handler(lambda c: c.data == "stop")
async def stop_sending(callback: types.CallbackQuery):
    global is_running, task
    is_running = False
    if task:
        task.cancel()
        task = None
    await callback.answer("🛑 Stopped.")

if __name__ == "__main__":
    executor.start_polling(dp)
