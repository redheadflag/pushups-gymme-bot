from re import Match
import logging

from aiogram import F, Router
from aiogram.types import Message, ReactionTypeEmoji
from sqlalchemy.ext.asyncio import AsyncSession

from bot.middlewares.user_context import UserContext
from core.config import settings
from db.commands import add_pushup_quantity_points, pushup_entry_repository
from db.models import PushupEntry


logger = logging.getLogger(__name__)


router = Router()


@router.message(
    F.reply_to_message,
    F.text.regexp(r"^\d*\.?\d+$").as_("quantity"),
    F.reply_to_message.content_type.in_(settings.ALLOWED_CONTENT_TYPES)
)
async def add_pushups_quantity(message: Message, session: AsyncSession, quantity: Match[str], user_context: UserContext):
    pushup_count = int(float(quantity.group()))
    replied_message = message.reply_to_message
    entry_date = replied_message.date.astimezone(settings.tzinfo).date()
    user_id = replied_message.from_user.id
    entry = await pushup_entry_repository.filter(
        session,
        PushupEntry.user_id == user_id,
        PushupEntry.date == entry_date
    )

    if len(entry) != 1:
        await message.reply("Запись не найдена :(")
        return

    entry = entry[0]
    entry.quantity = pushup_count
    await session.commit()

    user = await user_context.get_user(session)
    await add_pushup_quantity_points(session=session, quantity=pushup_count, user=user)
    await message.react(reaction=[ReactionTypeEmoji(emoji="👍")])
