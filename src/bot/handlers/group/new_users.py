from bot.filters.new_users import NewUserFilter
from bot.handlers.group.user_sends_video import user_sends_video_handler
from bot.middlewares.user_context import UserContext
from core import strings
from core.config import settings


from aiogram import F, Bot, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession


import asyncio


router = Router()

router.message.filter(NewUserFilter())


@router.message(F.content_type.in_(settings.ALLOWED_CONTENT_TYPES))
async def new_user_sends_video(message: Message, session: AsyncSession, user_context: UserContext, bot: Bot):
    await asyncio.sleep(1)
    await message.answer(strings.GREETING_MESSAGE_SENT_VIDEO.format(message.from_user.mention_html(message.from_user.first_name)))  # type: ignore

    await asyncio.sleep(1)
    await user_sends_video_handler(message=message, session=session, user_context=user_context, bot=bot)


@router.message()
async def message_new_user(message: Message, session: AsyncSession):
    await message.answer(strings.GREETING_MESSAGE_FIRST_MESSAGE.format(message.from_user.mention_html(message.from_user.first_name)))  # type: ignore