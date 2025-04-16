from aiogram import F, Router
from aiogram.enums import ChatType

from bot.handlers.group import user_sends_video


group_router = Router()
group_router.message.filter(F.chat.type == ChatType.SUPERGROUP)


group_router.include_router(user_sends_video.pushups_router)
