import asyncio
from datetime import time
import logging
from re import Match

from aiogram import F, Router
from aiogram.enums import ContentType
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.filters.new_users import IsNewUser
from core import strings
from core.config import settings
from core.utils import STREAK_FIRST_DAY_REACTION, bot_set_reaction
from db.commands import add_pushup_entry, pushup_entry_repository
from db.models import PushupEntry, User


logger = logging.getLogger(__name__)


pushups_router = Router()
pushups_router.message.filter(F.message_thread_id == settings.TOPIC_ID)


@pushups_router.message(
    F.content_type.in_([ContentType.VIDEO_NOTE, ContentType.VIDEO]),
    IsNewUser(is_new=False)
)
async def user_sends_video_handler(message: Message, session: AsyncSession, user: User):
    entry = await add_pushup_entry(session=session, user=user)
    if not entry:
        return
    
    if entry.timestamp > time(hour=23, minute=0):
        await message.reply(strings.last_chance_msg())
    
    if user.streak == 1:
        await message.reply(strings.STREAK_FIRST_DAY)
        await bot_set_reaction(
            message=message,
            reaction=STREAK_FIRST_DAY_REACTION,
            guaranteed=True
        )
    else:
        await bot_set_reaction(
            message=message,
            guaranteed=True
        )


@pushups_router.message(
    F.content_type.in_([ContentType.VIDEO_NOTE, ContentType.VIDEO]),
    IsNewUser(is_new=True)
)
async def new_user_sends_video(message: Message, session: AsyncSession, user: User):
    await asyncio.sleep(1)
    await message.answer(strings.GREETING_MESSAGE_SENT_VIDEO.format(message.from_user.mention_html(message.from_user.first_name)))  # type: ignore

    await asyncio.sleep(1)
    await user_sends_video_handler(message=message, session=session, user=user)


@pushups_router.message(
    IsNewUser(is_new=False),
    F.reply_to_message,
    F.text.regexp(r"^\d*\.?\d+$").as_("quantity")
)
async def add_pushups_quantity(message: Message, session: AsyncSession, quantity: Match[str]):
    replied_message = message.reply_to_message
    if not replied_message:
        return
    if replied_message.content_type not in [ContentType.VIDEO_NOTE, ContentType.VIDEO]:
        return
    entry_date = replied_message.date.astimezone(settings.tzinfo).date()
    entry = await pushup_entry_repository.filter(
        session,
        PushupEntry.user_id == replied_message.from_user.id,
        PushupEntry.date == entry_date
    )
    if len(entry) == 1:
        entry = entry[0]
        entry.quantity = int(float(quantity.group()))
        await session.commit()
        await message.reply("Добавил в статистику!")
    else:
        await message.reply("Запись не найдена :(")


@pushups_router.message(
    IsNewUser(is_new=True)
)
async def message_new_user(message: Message, session: AsyncSession, user: User):
    await message.answer(strings.GREETING_MESSAGE_FIRST_MESSAGE.format(message.from_user.mention_html(message.from_user.first_name)))  # type: ignore
