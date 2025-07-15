import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.token import TokenValidationError
from config import TOKEN

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

message_to_send = ""
send_interval = 60  # in seconds
is_running = False
task = None  # for loop control

# Create inline keyboard
def control_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶ Start", callback_data="start"),
         InlineKeyboardButton(text="⏹ Stop", callback_data="stop")]
    ])
    return keyboard

@dp.message(Command("start"))
async def cmd_start(msg: Message):
    await msg.answer(
        "Welcome! This bot sends a message automatically at the interval you choose.

Use:
- /add Your message
- /interval Number (minutes)

Then tap the buttons below:",
        reply_markup=control_keyboard()
    )

@dp.message(Command("add"))
async def cmd_add(msg: Message):
    global message_to_send
    text = msg.text.split(' ', 1)
    if len(text) < 2:
        await msg.answer("Use the command like this:
<code>/add Your message here</code>")
    else:
        message_to_send = text[1]
        await msg.answer(f"✅ Message set:

{message_to_send}")

@dp.message(Command("interval"))
async def cmd_interval(msg: Message):
    global send_interval
    text = msg.text.split()
    if len(text) < 2 or not text[1].isdigit():
        await msg.answer("Use the command like this:
<code>/interval 10</code>")
    else:
        send_interval = int(text[1]) * 60
        await msg.answer(f"✅ Interval set to {text[1]} minutes.")

@dp.callback_query(F.data == "start")
async def cb_start(callback: CallbackQuery):
    global is_running, task
    if not message_to_send:
        await callback.answer("Set a message first using /add.", show_alert=True)
        return
    if is_running:
        await callback.answer("Already running.", show_alert=True)
        return

    is_running = True
    await callback.answer("🚀 Started!")

    async def sending_loop():
        while is_running:
            await bot.send_message(callback.message.chat.id, message_to_send)
            await asyncio.sleep(send_interval)

    task = asyncio.create_task(sending_loop())

@dp.callback_query(F.data == "stop")
async def cb_stop(callback: CallbackQuery):
    global is_running, task
    is_running = False
    if task:
        task.cancel()
        task = None
    await callback.answer("🛑 Stopped.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
