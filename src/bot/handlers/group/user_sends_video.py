import logging
import random
from aiogram import F, Router
from aiogram.enums import ContentType
from aiogram.types import Message, ReactionTypeEmoji
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.utils import REACTION_LIST
from db.commands import add_or_update_user, add_pushup_entry


logger = logging.getLogger(__name__)


pushups_router = Router()
pushups_router.message.filter(F.message_thread_id == settings.TOPIC_ID)


@pushups_router.message(
        F.content_type.in_([ContentType.VIDEO_NOTE, ContentType.VIDEO])
)
async def user_sends_video_handler(message: Message, session: AsyncSession):
    data = {
        "id": message.from_user.id,
        "username": message.from_user.username,
        "full_name": message.from_user.full_name
    }
    user = await add_or_update_user(session=session, data=data)
    entry = await add_pushup_entry(session=session, user=user)
    if entry and random.random() < 0.2:
        is_big = random.random() < 0.2
        reaction = ReactionTypeEmoji(emoji=random.choice(REACTION_LIST))
        logger.info("Set reaction %s to message id=%i", reaction.emoji, message.message_id)
        await message.react(reaction=[reaction], is_big=is_big)
