import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import load_dotenv

import sys
import os
# Load .env from same directory as main.py
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

# Bot sozlamalari
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 123456789))
DB_NAME = "instance/edu_center_bot.db"

from database import init_db
from handlers.user_handlers import router as user_router
from handlers.admin_handlers import router as admin_router

# ── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Main ─────────────────────────────────────────────────────────────────────

async def main():
    # DB ni ishga tushirish
    init_db()

    # PythonAnywhere proxy (for free accounts)
    session = AiohttpSession(proxy="http://proxy.server:3128")
    bot = Bot(
        token=BOT_TOKEN, 
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Routerlarni ulash (admin birinchi – priority)
    dp.include_router(admin_router)
    dp.include_router(user_router)

    logger.info("Bot is starting...")

    # Eski update larni o'chirish
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
