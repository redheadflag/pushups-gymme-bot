import asyncio
from datetime import date, datetime, timedelta
import logging
import random
from typing import Sequence

from aiogram import Bot
from aiogram.exceptions import TelegramNotFound
from aiogram.types import Message, ReactionTypeEmoji
from sqlalchemy.ext.asyncio import AsyncSession


from core.config import settings
from core.strings import get_daily_report
from db.models import User


logger = logging.getLogger(__name__)

MESSAGE_SENDING_LATENCY = 1//20  # 20 messages per second

REACTION_LIST = ["❤", "🫡", "👍", "👀", "🥴", "🙈", "🍌", "⚡", "🔥", "🏆"]
WEIGHTS = [15, 4, 16, 1, 3, 1, 1, 3, 10, 3]

SPECIAL_REACTION = ReactionTypeEmoji(emoji="❤️‍🔥")


async def bot_set_reaction(message: Message, reaction: ReactionTypeEmoji | None = None, guaranteed: bool = True):
    if not guaranteed:
        if random.random() < 0.8:
            return
    
    is_big = random.random() < 0.2
    if not reaction:
        reaction = ReactionTypeEmoji(emoji=random.choices(REACTION_LIST, WEIGHTS, k=1)[0])
    logger.info("Set reaction %s to message id=%i", reaction.emoji, message.message_id)
    await message.react(reaction=[reaction], is_big=is_big)


async def send_daily_report(session: AsyncSession, bot: Bot, chat_id: int, dt: date, topic_id: int | None = None):
    from db.commands import (
        get_all_users_summary,
        get_early_bird_user,
        get_last_wagon_user,
        get_strongest_user
    )
    
    users = await get_all_users_summary(session=session)
    yesterday_date = dt - timedelta(days=1)

    early_bird_user = await get_early_bird_user(session, yesterday_date)
    strongest_user = await get_strongest_user(session, yesterday_date)
    last_wagon_user = await get_last_wagon_user(session, yesterday_date)

    text = get_daily_report(
        users_summary=users,
        dt=dt,
        early_bird_user=early_bird_user,
        strongest_user=strongest_user,
        last_wagon_user=last_wagon_user
    )
    
    await bot.send_message(chat_id=chat_id, message_thread_id=topic_id, text=text)


def get_current_datetime() -> datetime:
    return datetime.now(settings.tzinfo)


async def send_message_to_admins(bot: Bot, session: AsyncSession, text: str) -> None:
    from db.commands import get_admins
    
    admins = await get_admins(session)
    await send_message_to_users(bot, admins, text=text)


async def send_message_to_users(bot: Bot, users: Sequence[User], text: str):
    for user in users:
        try:
            await bot.send_message(chat_id=user.id, text=text)
        except TelegramNotFound:
            pass
        else:
            await asyncio.sleep(MESSAGE_SENDING_LATENCY)
