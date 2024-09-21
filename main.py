from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from routers import setup_routers
from utils.config import TELEGRAM_BOT_TOKEN
from utils.log import logger
import asyncio

async def main():
    """Function to run aiogram bot"""
    try:
        # Configure the aiogram bot with defaults
        bot = Bot(
            token=TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(
                parse_mode=ParseMode.MARKDOWN,
                link_preview_is_disabled=True
            )
        )

        # Set up Dispatcher with in-memory storage
        dp = Dispatcher(storage=MemoryStorage())
        # Set routers (handlers) for bot
        dp.include_router(setup_routers())
        # Delete pending messages
        await bot.delete_webhook(drop_pending_updates=True)
        # Start polling the bot
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f'An aiogram error occurred: {e}')

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning('Bot stopped by user.')