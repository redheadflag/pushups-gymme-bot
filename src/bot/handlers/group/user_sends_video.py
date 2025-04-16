import asyncio
import logging
import random
from aiogram import F, Router
from aiogram.enums import ContentType
from aiogram.types import Message, ReactionTypeEmoji, gift
from aiogram.utils.markdown import hlink
from sqlalchemy.ext.asyncio import AsyncSession

from bot.filters.new_users import IsNewUser
from core.config import settings
from core.utils import STREAK_FIRST_DAY_REACTION, bot_set_reaction
from db.commands import add_pushup_entry
from db.models import User


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
    
    if user.streak == 1:
        await message.reply("Добро пожаловать в клуб! 💪")
        await bot_set_reaction(
            message=message,
            emoji=STREAK_FIRST_DAY_REACTION,
            guaranteed=True
        )
    else:
        await bot_set_reaction(
            message=message,
            guaranteed=False
        )


@pushups_router.message(
    F.content_type.in_([ContentType.VIDEO_NOTE, ContentType.VIDEO]),
    IsNewUser(is_new=True)
)
async def new_user_sends_video(message: Message, session: AsyncSession, user: User):
    await asyncio.sleep(1)
    await message.answer(
        "\n\n".join([
            f"Привет, {message.from_user.mention_html(message.from_user.first_name)}!",  # type: ignore
            "Здесь мы делаем прокачиваемся каждый день, делая отжимания.",
            f"Как я вижу, ты сразу врываешься в бой. Достойно уважения! Но на всякий случай, ознакомься с {hlink("правилами", settings.RULES_URL)}"
        ]),
    )

    await asyncio.sleep(1)
    await user_sends_video_handler(message=message, session=session, user=user)


@pushups_router.message(
    IsNewUser(is_new=True)
)
async def message_new_user(message: Message, session: AsyncSession, user: User):
    await message.answer(
        "\n\n".join([
            f"Привет, {message.from_user.mention_html(message.from_user.first_name)}!",  # type: ignore
            "Здесь мы делаем прокачиваемся каждый день, делая отжимания.",
            f"Присоединяйся к нам! Но для начала, ознакомься с {hlink("правилами", settings.RULES_URL)}"
        ]),
    )

