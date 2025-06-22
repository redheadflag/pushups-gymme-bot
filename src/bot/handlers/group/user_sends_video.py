import asyncio
import logging
import re
from datetime import time

from aiogram import F, Router
from aiogram.enums import ContentType
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.enums import PointEvent
from bot.filters.new_users import IsNewUser
from core.utils import get_current_datetime
from core import strings
from core.config import settings
from core.utils import STREAK_FIRST_DAY_REACTION, bot_set_reaction
from db.commands import add_pushup_entry, add_points_transaction
from db.models import User


logger = logging.getLogger(__name__)


router = Router()


@router.message(
    F.content_type.in_(settings.ALLOWED_CONTENT_TYPES),
    IsNewUser(is_new=False)
)
async def user_sends_video_handler(message: Message, session: AsyncSession, user: User):
    entry = await add_pushup_entry(session=session, user=user)
    if not entry:
        return
    
    if message.content_type == ContentType.VIDEO \
            and message.caption \
            and re.fullmatch(r"^\d*\.?\d+$", message.caption):
        entry.quantity = int(message.caption)
        await session.commit()

    if entry.timestamp > time(hour=23, minute=55):
        await message.reply(strings.last_chance_msg())
    
    streak = await user.get_streak(session)
    
    if streak == 1:
        if user.created_at.astimezone(settings.tzinfo) == get_current_datetime().date:
            await message.reply(strings.STREAK_FIRST_DAY)
            await add_points_transaction(session, PointEvent.FIRST_PUSHUPS.value, user=user)
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
            await message.reply(strings.USER_WELCOME_BACK.format(user=str(user)))
    else:
        additional_message = str()
        if streak == 30:
            await add_points_transaction(session, PointEvent.STREAK_30_DAYS.value, user=user)
            additional_message = strings.STREAK_30_DAYS.format(user=str(user))
        elif streak == 100:
            await add_points_transaction(session, PointEvent.STREAK_100_DAYS.value, user=user)
            additional_message = strings.STREAK_100_DAYS.format(user=str(user))
        
        if additional_message != "":
            await message.reply(additional_message)
        
        await bot_set_reaction(
            message=message,
            guaranteed=True
        )


@router.message(
    F.content_type.in_(settings.ALLOWED_CONTENT_TYPES),
    IsNewUser(is_new=True)
)
async def new_user_sends_video(message: Message, session: AsyncSession, user: User):
    await asyncio.sleep(1)
    await message.answer(strings.GREETING_MESSAGE_SENT_VIDEO.format(message.from_user.mention_html(message.from_user.first_name)))  # type: ignore

    await asyncio.sleep(1)
    await user_sends_video_handler(message=message, session=session, user=user)


@router.message(
    IsNewUser(is_new=True)
)
async def message_new_user(message: Message, session: AsyncSession, user: User):
    await message.answer(strings.GREETING_MESSAGE_FIRST_MESSAGE.format(message.from_user.mention_html(message.from_user.first_name)))  # type: ignore
