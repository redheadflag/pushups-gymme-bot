from aiogram import F, Router
from aiogram.enums import ChatType

from bot.handlers.private import start


private_router = Router()
private_router.message.filter(F.chat.type == ChatType.PRIVATE)


private_router.include_routers(
    start.router
)
