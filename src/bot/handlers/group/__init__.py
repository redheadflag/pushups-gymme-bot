from aiogram import F, Router
from aiogram.enums import ChatType

from bot.handlers.group import commands, general, user_sends_collaboration, user_sends_quantity, user_sends_video, new_users
from bot.middlewares.events import EventMiddleware
from bot.middlewares.user_context import UserContextMiddleware
from core.config import settings


group_router = Router()
group_router.message.filter(F.chat.type == ChatType.SUPERGROUP)

general_group_router = Router()

general_group_router.include_routers(
    general.router
)

pushups_router = Router()

# Outer Middlewares
pushups_router.message.outer_middleware(UserContextMiddleware())

# Filters
pushups_router.message.filter(F.message_thread_id == settings.PUSHUPS_TOPIC_ID)

# Inner Middlewares
pushups_router.message.middleware(EventMiddleware())

pushups_router.include_routers(
    new_users.router,
    commands.command_router,
    user_sends_quantity.router,
    user_sends_video.router,
    user_sends_collaboration.router,
)

group_router.include_routers(
    general_group_router,
    pushups_router,
)
