from aiogram import F, Router
from aiogram.enums import ChatType

from bot.handlers.group import commands, user_sends_quantity, user_sends_video
from bot.middlewares.user import UserMiddleware
from core.config import settings


group_router = Router()
group_router.message.filter(F.chat.type == ChatType.SUPERGROUP)

pushups_router = Router()
pushups_router.message.outer_middleware(UserMiddleware())
pushups_router.message.filter(F.message_thread_id == settings.TOPIC_ID)

pushups_router.include_routers(
    commands.command_router,
    user_sends_quantity.router,
    user_sends_video.router
)

group_router.include_routers(
    pushups_router
)
