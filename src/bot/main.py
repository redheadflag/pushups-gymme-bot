import asyncio

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from bot.bot_instance import bot
from bot.handlers.private import private_router
from bot.handlers.group import group_router
from bot.middlewares.db import DbSessionMiddleware
from core.redis import redis
from core.logging import setup_logging
from db.base import sessionmaker


async def main():
    setup_logging()

    dp = Dispatcher(storage=RedisStorage(redis))

    dp.include_routers(
        private_router,
        group_router
    )
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
