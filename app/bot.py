from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from environs import Env

env = Env()
env.read_env()
API_TOKEN = env.str("API_TOKEN")
CHAT_ID = env.str("CHAT_ID")
WEBHOOK_URL = env.str("WEBHOOK_URL")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Salom! /start ishlayapti ✅")


dp.include_router(router)

async def setup_webhook():
    await bot.set_webhook(
        url=WEBHOOK_URL,
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True,
    )