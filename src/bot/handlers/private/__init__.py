from aiogram import F, Router
from aiogram.enums import ChatType

from bot.handlers.private import start
from bot.middlewares.throttling import ThrottlingMiddleware
from core.redis import redis


private_router = Router()
private_router.message.filter(F.chat.type == ChatType.PRIVATE)
private_router.message.middleware(ThrottlingMiddleware(redis=redis))


private_router.include_routers(
    start.router
)
