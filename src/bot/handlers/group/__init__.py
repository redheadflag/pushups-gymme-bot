from aiogram import F, Router
from aiogram.enums import ChatType

from bot.handlers.group import commands, user_sends_video
from bot.middlewares.user import UserMiddleware


group_router = Router()
group_router.message.outer_middleware(UserMiddleware())
group_router.message.filter(F.chat.type == ChatType.SUPERGROUP)


group_router.include_routers(
    commands.command_router,
    user_sends_video.pushups_router,
)
